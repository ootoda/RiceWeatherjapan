import pygame
import random
import time
import os
import math
import csv
from typing import Dict, List, Tuple, Optional
from PIL import Image

class NewsItem:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content

class Character:
    def __init__(self, name: str, role: str, image_path: str):
        self.name = name
        self.role = role
        self.image_path = image_path
        self.image = None
    
    def get_message(self, price: int, month: int) -> str:
        """価格と月に応じてキャラクターのメッセージを生成"""
        if self.role == "主婦":
            return self._housewife_message(price, month)
        elif self.role == "農家":
            return self._farmer_message(price, month)
        elif self.role == "政治家":
            return self._politician_message(price, month)
    
    def _housewife_message(self, price: int, month: int) -> str:
        if price < 300:
            messages = [
                "お米が安くて助かる！家計が楽になるの。",
                "この価格なら子供たちにたくさん食べさせられる！",
                "安いお米で今月は贅沢できそう♪"
            ]
        elif price < 500:
            messages = [
                "まあまあの値段ね。家計を考えると普通かしら。",
                "この価格なら我慢できる範囲ね。",
                "もう少し安くなってくれるといいんだけど..."
            ]
        else:
            messages = [
                "お米が高すぎる！家計が大変よ！",
                "この値段じゃ節約しないと。パンに変えようかしら。",
                "政府は何をしているの！生活が苦しいわ！"
            ]
        return random.choice(messages)
    
    def _farmer_message(self, price: int, month: int) -> str:
        if price < 300:
            messages = [
                "価格が安すぎる！これじゃ生活できないよ！",
                "こんな安値じゃ農業を続けられない...",
                "コストを考えると赤字だ。政府の支援が必要だ。"
            ]
        elif price < 500:
            messages = [
                "まあまあの価格だな。なんとか生活できる。",
                "この価格なら農業を続けられそうだ。",
                "もう少し高くなってくれるとありがたいが..."
            ]
        else:
            messages = [
                "いい価格だ！これで投資もできる！",
                "高値で助かる！新しい設備を導入しよう。",
                "この調子で価格が安定してくれるといいな。"
            ]
        return random.choice(messages)
    
    def _politician_message(self, price: int, month: int) -> str:
        if price < 300:
            messages = [
                "価格安定化のため農家支援策を検討します。",
                "消費者には朗報ですが、生産者支援が必要ですね。",
                "市場介入を検討する時期かもしれません。"
            ]
        elif price < 500:
            messages = [
                "適正価格を維持しており、政策は順調です。",
                "バランスの取れた価格帯を維持しています。",
                "現在の政策を継続して参ります。"
            ]
        else:
            messages = [
                "高騰抑制策を緊急に検討いたします。",
                "消費者負担軽減のため対策を講じます。",
                "価格安定化に向けて全力で取り組みます。"
            ]
        return random.choice(messages)

class RiceGameWindow:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ファミコン風米価格アドベンチャー")
        
        # 日本語フォント設定 - PressStart2Pを優先
        self.font_large = self.load_japanese_font(40)
        self.font_medium = self.load_japanese_font(36)
        self.font_small = self.load_japanese_font(34)
        
        # 色定義（ファミコン風カラーパレット）
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'blue': (0, 88, 248),
            'green': (0, 168, 0),
            'red': (248, 56, 0),
            'yellow': (252, 252,  6),
            'gray': (128, 128, 128),
            'dark_blue': (0, 0, 128),
            'text_bg': (24, 24, 88),
            'news_bg': (88, 24, 24)  # ニュース用背景色
        }
        
        # ゲーム状態
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_month = 1
        self.rice_price = 400
        self.last_update = time.time()
        
        # ニュースシステム
        self.news_items = []
        self.load_news_csv()
        self.showing_news = False
        self.current_news = None
        self.news_start_time = 0
        self.news_duration = 6.0  # ニュース表示時間（4秒）
        self.character_message_duration = 5.0  # キャラクター会話時間（5秒）
        
        # キャラクター設定
        self.characters = [
            Character("田中さん", "主婦", "images/housewife.png"),
            Character("山田さん", "農家", "images/farmer.png"),
            Character("佐藤議員", "政治家", "images/politician.png")
        ]
        self.current_speaker = 0
        
        # テキスト表示用
        self.current_message = ""
        self.display_message = ""
        self.message_index = 0
        self.last_char_time = 0
        self.char_delay = 100  # ミリ秒
        
        # 画像フォルダ
        self.image_folders = {
            'characters': 'images/characters/',
            'backgrounds': 'images/backgrounds/',
            'rice': 'images/rice/',
            'ui': 'images/ui/'
        }

        # --- Sound Setup ---
        try:
            pygame.mixer.init() # Initialize the mixer module
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"Error initializing pygame mixer: {e}")
            print("Sound playback will be disabled.")
            self.mixer_available = False
        else:
            self.mixer_available = True

        # Define sound file paths (assuming a 'sounds' folder)
        self.sound_files = {
            "month_change": "sounds/month_change.wav",
            "text_click": "sounds/text_click.wav",
            "background_music": "sounds/background_music.mp3",
            "news_alert": "sounds/news_alert.wav"  # ニュース開始音
        }
        self.loaded_sounds = {}
        self.load_sounds()
        # --- End Sound Setup ---
        
        # 背景画像（季節別）
        self.background_images = {}
        self.load_resources()
    
    def load_news_csv(self):
        """news.csvからニュース項目を読み込み"""
        csv_path = "news.csv"
        self.news_items = []
        
        if not os.path.exists(csv_path):
            print(f"警告: {csv_path}が見つかりません。ニュース機能は無効になります。")
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader, None)  # ヘッダー行をスキップ
                
                for row in csv_reader:
                    if len(row) >= 4:  # C列（インデックス2）とD列（インデックス3）が存在することを確認
                        name = row[2].strip()  # C列：名前
                        content = row[3].strip()  # D列：本文
                        
                        if name and content:  # 空でない場合のみ追加
                            self.news_items.append(NewsItem(name, content))
            
            print(f"ニュース項目を{len(self.news_items)}件読み込みました。")
            
        except Exception as e:
            print(f"news.csvの読み込み中にエラーが発生しました: {e}")
    
    def should_show_news(self) -> bool:
        """ニュースを表示するかどうかを決定（10-36%の確率）"""
        if not self.news_items:
            return False
        
        probability = random.randint(10, 36)
        return random.randint(1, 100) <= probability
    
    def select_random_news(self) -> Optional[NewsItem]:
        """ランダムなニュース項目を選択"""
        if not self.news_items:
            return None
        return random.choice(self.news_items)
    
    def load_sounds(self):
        """Loads sound files into the mixer."""
        if not self.mixer_available:
            return

        for name, path in self.sound_files.items():
            if os.path.exists(path):
                try:
                    if name == "background_music":
                        # For background music, we'll load it directly in play_background_music
                        pass
                    else:
                        self.loaded_sounds[name] = pygame.mixer.Sound(path)
                        print(f"Loaded sound: {name} from {path}")
                except pygame.error as e:
                    print(f"Error loading sound file {path}: {e}")
            else:
                print(f"Sound file not found: {path}")

    def play_sound_effect(self, sound_name: str):
        """Plays a sound effect if the mixer is available and the sound is loaded."""
        if not self.mixer_available:
            return
        
        if sound_name in self.loaded_sounds:
            try:
                self.loaded_sounds[sound_name].play()
            except pygame.error as e:
                print(f"Error playing sound effect '{sound_name}': {e}")
        else:
            print(f"Sound effect '{sound_name}' not found or not loaded.")

    def play_background_music(self):
        """Plays the background music, looping indefinitely, if mixer is available."""
        if not self.mixer_available:
            return

        music_path = self.sound_files.get("background_music")
        if music_path and os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1) # -1 for infinite loop
                print(f"Playing background music: {music_path}")
            except pygame.error as e:
                print(f"Error playing background music {music_path}: {e}")
        else:
            print("Background music file not found or not specified.")

    def stop_background_music(self):
        """Stops the background music if the mixer is available."""
        if self.mixer_available:
            pygame.mixer.music.stop()
            print("Background music stopped.")

    def load_resources(self):
        """リソースを読み込み"""
        # フォルダが存在しない場合は作成
        for folder in self.image_folders.values():
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        # 画像読み込み（存在する場合）
        try:
            # キャラクター画像の読み込み
            for char in self.characters:
                if os.path.exists(char.image_path):
                    char.image = pygame.image.load(char.image_path)
                    char.image = pygame.transform.scale(char.image, (120, 120))
            
            # 背景画像の読み込み（季節別）
            seasons = ['spring', 'summer', 'autumn', 'winter']
            for season in seasons:
                bg_path = os.path.join(self.image_folders['backgrounds'], f"{season}.png")
                if os.path.exists(bg_path):
                    self.background_images[season] = pygame.image.load(bg_path)
                    self.background_images[season] = pygame.transform.scale(
                        self.background_images[season], (self.width, self.height)
                    )
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
    
    def load_japanese_font(self, size: int):
        """日本語フォントを読み込み (x12y16pxMaruMonica.ttfを優先)"""
        font_paths_to_try = [
            # 優先度1: PressStart2P (ファミコン風)
            os.path.join('fonts', 'x12y16pxMaruMonica.ttf'),
            
            # 優先度2: システムフォント（Windows, macOS, Linux）
            # Windows
            "C:/Windows/Fonts/msgothic.ttc",  # MS Gothic
            "C:/Windows/Fonts/msmincho.ttc",  # MS Mincho
            "C:/Windows/Fonts/meiryo.ttc",    # Meiryo
            "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        
        for font_path in font_paths_to_try:
            try:
                if os.path.exists(font_path):
                    print(f"フォントを読み込み中: {font_path}")
                    return pygame.font.Font(font_path, size)
            except Exception as e:
                print(f"フォント '{font_path}' の読み込みに失敗しました: {e}")
                continue
        
        # フォールバック: システムフォントから日本語対応フォントを探す
        try:
            print("システムフォントから日本語フォントを検索します...")
            available_fonts = pygame.font.get_fonts()
            japanese_fonts = [
                'msgothic', 'msmincho', 'meiryo', 'notosanscjk',
                'hiraginokakugothicpro', 'hiraginominchopro',
                'takao', 'ipa', 'vlgothic', 'arial unicode ms'
            ]
            
            for jp_font in japanese_fonts:
                if jp_font in available_fonts:
                    print(f"システムフォント '{jp_font}' を使用します。")
                    return pygame.SysFont(jp_font, size)
            
            print("日本語対応システムフォントが見つかりません。デフォルトフォントを使用します。")
            return pygame.font.Font(None, size)
        except Exception as e:
            print(f"システムフォントの検索中にエラーが発生しました: {e}")
            print("デフォルトフォントを使用します。")
            return pygame.font.Font(None, size)
    
    def get_season(self, month: int) -> str:
        """月から季節を取得"""
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def update_price(self):
        """価格を更新（タイミング調整版）"""
        current_time = time.time()
        
        # ニュース表示中の場合
        if self.showing_news:
            if current_time - self.news_start_time >= self.news_duration:
                # ニュース終了、キャラクター会話に移行
                self.showing_news = False
                self.current_news = None
                self.set_new_message()
                self.character_start_time = current_time  # キャラクター会話の開始時間を記録
            return
        
        # キャラクター会話中で、ニュースの後の場合
        if hasattr(self, 'character_start_time') and self.character_start_time > 0:
            if current_time - self.character_start_time >= self.character_message_duration:
                # キャラクター会話終了、月を切り替える
                self.advance_month(current_time)
                self.character_start_time = 0  # リセット
            return
        
        # 通常の月更新タイミング（ニュースがなかった場合）
        if current_time - self.last_update >= self.character_message_duration:
            self.advance_month(current_time)
    
    def advance_month(self, current_time):
        """月を進める処理"""
        # 月を進める
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
        
        # 価格を変動させる（季節要因も考慮）
        season_factor = self.get_season_price_factor()
        base_change = random.randint(-100, 100)
        seasonal_change = season_factor * random.randint(-50, 50)
        
        self.rice_price += int(base_change + seasonal_change)
        self.rice_price = max(200, min(800, self.rice_price))  # 価格範囲制限
        
        # 月変更音
        self.play_sound_effect("month_change")
        
        # ニュースを表示するかチェック
        if self.should_show_news():
            self.current_news = self.select_random_news()
            if self.current_news:
                self.showing_news = True
                self.news_start_time = current_time
                self.display_message = ""
                self.message_index = 0
                
                # ニュースアラート音
                self.play_sound_effect("news_alert")
                print(f"ニュースを表示中: {self.current_news.name}")
            else:
                # ニュースがない場合は通常のキャラクター会話
                self.set_new_message()
                self.last_update = current_time
        else:
            # ニュースを表示しない場合は通常のキャラクター会話
            self.set_new_message()
            self.last_update = current_time
    
    def get_season_price_factor(self) -> float:
        """季節による価格変動係数"""
        season = self.get_season(self.current_month)
        factors = {
            'spring': 0.8,  # 春：やや安定
            'summer': 1.2,  # 夏：やや高め
            'autumn': 0.6,  # 秋：収穫期で安め
            'winter': 1.0   # 冬：通常
        }
        return factors.get(season, 1.0)
    
    def set_new_message(self):
        """新しいメッセージを設定"""
        speaker = self.characters[self.current_speaker]
        self.current_message = speaker.get_message(self.rice_price, self.current_month)
        self.display_message = ""
        self.message_index = 0
        
        # 次の話者に変更
        self.current_speaker = (self.current_speaker + 1) % len(self.characters)
    
    def update_text_display(self):
        """テキストを一文字ずつ表示"""
        current_time = pygame.time.get_ticks()
        
        if self.showing_news and self.current_news:
            # ニューステキストの表示
            full_news_text = f"【{self.current_news.name}】{self.current_news.content}"
            if (self.message_index < len(full_news_text) and 
                current_time - self.last_char_time > self.char_delay):
                
                self.display_message += full_news_text[self.message_index]
                self.message_index += 1
                self.last_char_time = current_time
                
                # テキスト音効果
                self.play_sound_effect("text_click")
        else:
            # 通常のキャラクター会話
            if (self.message_index < len(self.current_message) and 
                current_time - self.last_char_time > self.char_delay):
                
                self.display_message += self.current_message[self.message_index]
                self.message_index += 1
                self.last_char_time = current_time
                
                # テキスト音効果
                self.play_sound_effect("text_click")
    
    def draw_text_window(self):
        """ファミコン風テキストウィンドウを描画"""
        # ウィンドウの位置とサイズ
        window_rect = pygame.Rect(50, 400, self.width - 100, 150)
        border_rect = pygame.Rect(45, 395, self.width - 90, 160)
        
        # ニュース表示時は背景色を変更
        bg_color = self.colors['news_bg'] if self.showing_news else self.colors['text_bg']
        
        # ボーダーとウィンドウ背景
        pygame.draw.rect(self.screen, self.colors['white'], border_rect)
        pygame.draw.rect(self.screen, bg_color, window_rect)
        
        # 内側のボーダー
        inner_border = pygame.Rect(45, 395, self.width - 90, 160)
        pygame.draw.rect(self.screen, self.colors['white'], inner_border, 2)
        
        if self.showing_news and self.current_news:
            # ニュース表示
            news_label = self.font_medium.render("【 ニュース速報 】", True, self.colors['yellow'])
            self.screen.blit(news_label, (70, 405))
        else:
            # 話者名表示
            speaker = self.characters[(self.current_speaker - 1) % len(self.characters)]
            speaker_text = self.font_medium.render(f"{speaker.name}（{speaker.role}）", 
                                                 True, self.colors['yellow'])
            self.screen.blit(speaker_text, (70, 405))
        
        # メッセージテキスト表示（複数行対応）445は表示の高さの位置 2行目の高さは45
        lines = self.wrap_text(self.display_message, self.width - 140)
        y_offset = 445
        for line in lines:
            if y_offset < 540:  # ウィンドウ内に収まる範囲
                text_surface = self.font_small.render(line, True, self.colors['white'])
                self.screen.blit(text_surface, (70, y_offset))
                y_offset += 45
    
    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを指定幅で折り返し"""
        words = text
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            text_width = self.font_small.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def draw_ui(self):
        """UI要素を描画"""
        # タイトル
        title = self.font_large.render("Rice Weather Japan", True, self.colors['white'])
        title_rect = title.get_rect(center=(self.width // 2, 30))
        self.screen.blit(title, title_rect)
        
        # 月表示
        month_text = self.font_medium.render(f"{self.current_month}月", True, self.colors['white'])
        self.screen.blit(month_text, (50, 70))
        
        # 価格表示
        price_text = self.font_medium.render(f"米価格: ¥{self.rice_price}/kg", 
                                           True, self.colors['green'])
        self.screen.blit(price_text, (140, 70))
        
        # ニュース表示中の表示
        if self.showing_news:
            news_indicator = self.font_small.render("【新しいトピックです】", True, self.colors['red'])
            self.screen.blit(news_indicator, (70, 350))
        
        # 価格グラフ（簡易版）
        self.draw_price_indicator()
        
        # キャラクター表示
        self.draw_characters()
    
    def draw_price_indicator(self):
        """価格インジケーターを描画"""
        indicator_rect = pygame.Rect(400, 87, 250, 20)
        pygame.draw.rect(self.screen, self.colors['gray'], indicator_rect)
        
        # 価格に応じた色分け
        price_ratio = (self.rice_price - 200) / 600  # 200-800の範囲を0-1に正規化
        if price_ratio < 0.33:
            color = self.colors['blue']  # 安い
        elif price_ratio < 0.66:
            color = self.colors['green']  # 適正
        else:
            color = self.colors['red']  # 高い
        
        fill_width = int(240 * price_ratio)
        fill_rect = pygame.Rect(405, 92, fill_width, 10)
        pygame.draw.rect(self.screen, color, fill_rect)
    
    def draw_characters(self):
        """キャラクターを描画"""
        char_positions = [(150, 190), (350, 190), (550, 190)]
        
        for i, char in enumerate(self.characters):
            x, y = char_positions[i]
            
            # キャラクター画像（または代替矩形）
            if char.image:
                self.screen.blit(char.image, (x, y))
            else:
                # 画像がない場合の代替表示
                char_rect = pygame.Rect(x, y, 120, 120)
                colors = [self.colors['red'], self.colors['green'], self.colors['blue']]
                pygame.draw.rect(self.screen, colors[i], char_rect)
                
                # キャラクター名
                name_text = self.font_small.render(char.role, True, self.colors['white'])
                name_rect = name_text.get_rect(center=(x + 60, y + 60))
                self.screen.blit(name_text, name_rect)
            
            # 現在の話者をハイライト（ニュース表示中は無効）8はボーダーの太さ
            if not self.showing_news and i == (self.current_speaker - 1) % len(self.characters):
                highlight_rect = pygame.Rect(x - 10, y - 10, 140, 140)
                pygame.draw.rect(self.screen, self.colors['yellow'], highlight_rect, 16)
    
    def draw_background(self):
        """背景を描画"""
        season = self.get_season(self.current_month)
        
        if season in self.background_images:
            self.screen.blit(self.background_images[season], (0, 0))
        else:
            # 背景画像がない場合のグラデーション背景
            season_colors = {
                'spring': (100, 200, 100),
                'summer': (100, 150, 250),
                'autumn': (200, 150, 100),
                'winter': (150, 150, 200)
            }
            bg_color = season_colors.get(season, (50, 50, 100))
            self.screen.fill(bg_color)
    
    def run(self):
        """メインゲームループ"""
        # 初期メッセージ設定
        self.set_new_message()
        
        # Play background music
        self.play_background_music()
        
        while self.running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # スペースキーで次のメッセージ
                        if self.showing_news:
                            if self.message_index >= len(f"【{self.current_news.name}】{self.current_news.content}"):
                                # ニュース表示を強制終了してキャラクター会話へ
                                self.showing_news = False
                                self.current_news = None
                                self.set_new_message()
                            else:
                                # ニュースメッセージを即座に全表示
                                full_text = f"【{self.current_news.name}】{self.current_news.content}"
                                self.display_message = full_text
                                self.message_index = len(full_text)
                        else:
                            if self.message_index >= len(self.current_message):
                                self.set_new_message()
                            else:
                                # メッセージを即座に全表示
                                self.display_message = self.current_message
                                self.message_index = len(self.current_message)
            
            # ゲーム状態更新
            self.update_price()
            self.update_text_display()
            
            # 描画
            self.draw_background()
            self.draw_ui()
            self.draw_text_window()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        # Stop background music before quitting
        self.stop_background_music()
        pygame.quit()

def main():
    """メイン関数"""
    print("=== ファミコン風米価格アドベンチャー v1.7 ===")
    print("新機能: ニュースCSV連携")
    print("")
    print("使用方法:")
    print("- ゲームは自動で進行し、通常は5秒ごとに月が変わります")
    print("- 月の切り替わり時、10-36%の確率でニュースが表示されます")
    print("- ニュースは4秒間表示され、その後キャラクター会話が5秒間表示されます")
    print("- スペースキーでメッセージを進められます")
    print("")
    print("必要ファイル:")
    print("- news.csv: C列に名前、D列に本文を記載")
    print("- 画像フォルダ構成:")
    print("  images/characters/ - キャラクター画像")
    print("  images/backgrounds/ - 背景画像（spring.png, summer.png, autumn.png, winter.png）")
    print("  images/rice/ - 米関連画像")
    print("  images/ui/ - UI要素画像")
    print("- 音声ファイルは 'sounds' フォルダに .mp3 または .wav 形式で配置してください。")
    print("  (例: sounds/month_change.mp3, sounds/text_click.mp3, sounds/background_music.mp3, sounds/news_alert.mp3)")
    print("")
    print("※ 画像ファイルが見つからない場合は代替表示されます")
    print("※ news.csvが見つからない場合、ニュース機能は無効になります")
    print("")
    print("フォント確認:")
    
    # フォント確認 (main関数内でpygame.init()を再度呼ぶのは避ける)
    # pygame.init()はRiceGameWindowの__init__で一度だけ呼ばれます。
    # ここでは、フォントが正しくロードされるかどうかの確認メッセージを表示します。
    
    # 実際のフォントロードはRiceGameWindowの__init__で行われます。
    # ここでは、PressStart2P.ttfが'fonts'フォルダに存在するかどうかをチェックする例を示します。
    font_check_path = os.path.join('fonts', 'PressStart2P.ttf')
    if os.path.exists(font_check_path):
        print(f"- \"{font_check_path}\" が見つかりました。ファミコン風フォントとして使用を試みます。")
    else:
        print(f"- \"{font_check_path}\" が見つかりません。システムフォントまたはデフォルトフォントを使用します。")
        print("  ファミコン風フォントを使用するには、'fonts'フォルダを作成し、その中に'PressStart2P.ttf'を配置してください。")
    
    # CSVファイル確認
    if os.path.exists("news.csv"):
        print("- \"news.csv\" が見つかりました。ニュース機能が有効になります。")
    else:
        print("- \"news.csv\" が見つかりません。ニュース機能は無効になります。")
        print("  CSVファイルのC列に「名前」、D列に「本文」を記載してください。")
    
    print("\nゲームを開始します...")
    
    game = RiceGameWindow()
    game.run()

if __name__ == "__main__":
    main()