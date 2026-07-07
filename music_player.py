import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import pygame
from PIL import Image, ImageTk, ImageDraw
import io
from mutagen.id3 import ID3, APIC
from colorthief import ColorThief
import math
import numpy as np
import json
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Music player :D")
        self.geometry("1000x680")
        self.minsize(800, 500)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── Sidebar ──────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color="#290843", corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=0)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_rowconfigure(3, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(self.sidebar, text="♫  Library",
                                   font=ctk.CTkFont(size=20, weight="bold"),
                                   text_color="#d4aaff", anchor="w")
        self.header.grid(row=0, column=0, sticky="new", padx=16, pady=(20, 8))

        self.addB = ctk.CTkButton(self.sidebar, text="＋  Add Local Music",
                                  font=ctk.CTkFont(size=14),
                                  height=38, fg_color="#2d1054",
                                  hover_color="#3d1a6e", text_color="#d4aaff",
                                  corner_radius=10,
                                  anchor="w", command=self._add_files)
        self.addB.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        self.playlist_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.playlist_frame.grid(row=3, column=0, sticky="nsew", padx=4, pady=4)
        self.playlist_frame.grid_columnconfigure(0, weight=1)

        # ── Main panel ───────────────────────────────────────────────────
        self.main_panel = ctk.CTkFrame(self, fg_color="#0d0d0d", corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        self.bg_canvas = tk.Canvas(self.main_panel, highlightthickness=0, bd=0, bg="#0d0d0d")
        self.bg_canvas.grid(row=0, column=0, sticky="nsew")
        self.bg_canvas.bind("<Configure>", self._size_em)

        # canvas items — drawn in order (back to front)
        self.bg_image_id  = self.bg_canvas.create_image(0, 0, anchor="nw")
        self.disk_image_id = self.bg_canvas.create_image(0, 0, anchor="center")
        self.title_id = self.bg_canvas.create_text(0, 0, text="Select a track",
                                                    fill="#ffffff",
                                                    font=("Helvetica", 16, "bold"),
                                                    anchor="center")
        self.artist_id = self.bg_canvas.create_text(0, 0, text="",
                                                     fill="#cccccc",
                                                     font=("Helvetica", 12),
                                                     anchor="center")
        self.play_button = self.bg_canvas.create_text(0,0,text ="⏸",    font=("Helvetica",60),fill="#ffffff",anchor="center",tags="play_button")
        self.bg_canvas.tag_bind("play_button","<Button-1>", lambda e: self.PlayIt())
        self.prev_button=self.bg_canvas.create_text(0,0,text ="⏮",font=("Helvetica",46),fill="#ffffff",anchor="center",tags="prev_button")
        self.bg_canvas.tag_bind("prev_button","<Button-1>", lambda e: self._prev())
        self.nxt_button=self.bg_canvas.create_text(0,0,text ="⏭",font=("Helvetica",46),fill="#ffffff",anchor="center",tags="nxt_button")
        self.bg_canvas.tag_bind("nxt_button","<Button-1>", lambda e: self._next())
        self.wave_played   = self.bg_canvas.create_line(0, 0, 0, 0, fill="#ffffff", width=3, smooth=True)
        self.wave_unplayed = self.bg_canvas.create_line(0, 0, 0, 0, fill="#555555", width=3, smooth=True)
        self.scrubber_label = self.bg_canvas.create_text(0, 0, text="PROGRESS",
                                                  fill="#666666",
                                                  font=("Helvetica", 9),
                                                  anchor="center")
        self.time_text= self.bg_canvas.create_text(0,0,text="0:00/0:00",fill="#cccccc",
                                                   font=("Helvetica,",11),anchor="center")
        self.wave_offset= 0.0

        


        # ── State ────────────────────────────────────────────────────────
        self.playlist      = []
        self.current_index = -1
        self.disk_angle    = 0.0
        self.disk_image    = None   # PIL RGBA disk
        self.disk_spin     = False

        self.bg_current = (13, 13, 13)
        self.bg_target  = (13, 13, 13)
        self.bg_t       = 1.0       # transition 0→1
        self.bg_offset  = 0.0
        self.bg_photo   = None
        self.disk_photo  = None
        self.frame_count = 0

        self.cx = 500   # canvas center x
        self.cy = 300   # canvas center y
        self.save_file=Path("playlist.json")
        self.track_end= False


        self.shuffle = False
        self.repeat = 0
        self.shffle = self.bg_canvas.create_text(0,0,text="⇌",font=("Helavetica",40),fill="#ffffff",anchor="center",tags="shffle")
        self.bg_canvas.tag_bind("shffle","<Button-1>", lambda e: self._shuffleForMebaby())
        self.rpt=    self.bg_canvas.create_text(0,0,text="↺",font=("Helavetica",40),fill="#ffffff",anchor="center",tags="rpt")
        self.bg_canvas.tag_bind("rpt","<Button-1>", lambda e: self._saythatagain())
        self.vol= ctk.CTkSlider(self.bg_canvas,from_=0,to=1,
                                width=200,height=14,
                                button_length=0,
                                progress_color="#ffffff",
                                fg_color="#333333",
                                button_color="#ffffff",
                                button_hover_color="#cccccc",
                                command=self._volume)
        self.search= ctk.CTkEntry(self.sidebar,placeholder_text="Search Songs",
                                  height=36,
                                  fg_color="#a76DEF",border_color="#3d1a6e",text_color="#212020",
                                  placeholder_text_color="#4B4B4B",corner_radius=10)
        self.search.grid(row=2,column=0,sticky ="ew",padx=12,pady=(0,8))
        self.search.bind("<Return>", lambda e: self._sail_the_seas())


        self.vol_low  = self.bg_canvas.create_text(0, 0, text="🔈",
                                            font=("Helvetica", 24),
                                            fill="#888888", anchor="center")
        self.vol_high = self.bg_canvas.create_text(0, 0, text="🔊",
                                            font=("Helvetica", 24),
                                            fill="#888888", anchor="center")
        


        pygame.mixer.init()
        self._load_songs()  
        self._loop()  
        self.vol.set(1)
        pygame.mixer.music.set_volume(1)
        self.vol_window=self.bg_canvas.create_window(0,0,anchor="center",
                                                     window=self.vol)  # single unified animation loop

    # ── Unified animation loop 
    def _loop(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()

        self.frame_count +=1
        if self.frame_count %3==0:
            self._bkgrnd(w,h)
        if self.disk_spin and self.disk_image:
            self._disk()

        self.after(16, self._loop)   # ~30fps
        self._wiggleIt()
        if self.current_index >= 0 and self.disk_spin:
            if not pygame.mixer.music.get_busy():
                self.disk_spin= False
                self.track_end = True
        
        if self.track_end:
            self.track_end=False
            self._next()


    def _bkgrnd(self, w, h):
       
        if self.bg_t < 1.0:
            self.bg_t = min(1.0, self.bg_t + 0.03)
        t = self.bg_t
        r = int(self.bg_current[0] + (self.bg_target[0] - self.bg_current[0]) * t)
        g = int(self.bg_current[1] + (self.bg_target[1] - self.bg_current[1]) * t)
        b = int(self.bg_current[2] + (self.bg_target[2] - self.bg_current[2]) * t)
        col = (r, g, b)

        # animated vertical sine wave gradient
        self.bg_offset = (self.bg_offset + 2) % h
        y_idx = (np.arange(h) + int(self.bg_offset)) % h
        wave  = 0.5 + 0.5 * np.sin(y_idx / h * math.pi * 2)

        # two-layer look: base dark + wave highlight
        red   = np.clip(col[0] * (0.3 + 0.7 * wave), 0, 255).astype(np.uint8)
        green = np.clip(col[1] * (0.3 + 0.7 * wave), 0, 255).astype(np.uint8)
        blue  = np.clip(col[2] * (0.3 + 0.7 * wave), 0, 255).astype(np.uint8)

        arr = np.stack([red, green, blue], axis=-1)
        arr = np.repeat(arr[:, np.newaxis, :], w, axis=1)

        img = Image.fromarray(arr, "RGB")
        self.bg_photo = ImageTk.PhotoImage(img)
        self.bg_canvas.itemconfigure(self.bg_image_id, image=self.bg_photo)

    def _disk(self):
        self.disk_angle = (self.disk_angle + 4) % 360
        rotated = self.disk_image.rotate(-self.disk_angle, resample=Image.BICUBIC)
        self.disk_photo = ImageTk.PhotoImage(rotated)
        self.bg_canvas.itemconfigure(self.disk_image_id, image=self.disk_photo)
        self.bg_canvas.coords(self.disk_image_id, self.cx, self.cy - 40)

    def _size_em(self, event):
        self.cx = event.width  // 2
        self.cy = event.height // 2
        self.bg_canvas.coords(self.disk_image_id, self.cx, self.cy - 80)
        self.bg_canvas.coords(self.title_id,  self.cx, self.cy + 165)
        self.bg_canvas.coords(self.artist_id, self.cx, self.cy + 185)
        self.bg_canvas.coords(self.scrubber_label,self.cx,self.cy+205 )
        self.bg_canvas.coords(self.time_text,self.cx,self.cy+250)
        self.bg_canvas.coords(self.play_button, self.cx, self.cy + 305)
        self.bg_canvas.coords(self.prev_button, self.cx - 120, self.cy + 305)
        self.bg_canvas.coords(self.nxt_button, self.cx + 120, self.cy + 305)
        self.bg_canvas.coords(self.shffle, self.cx - 180, self.cy + 305)
        self.bg_canvas.coords(self.rpt, self.cx + 180, self.cy + 305)
        self.bg_canvas.coords(self.vol_window,self.cx,self.cy+380)
        self.bg_canvas.coords(self.vol_low,  self.cx - 140, self.cy + 380)
        self.bg_canvas.coords(self.vol_high, self.cx + 140, self.cy + 380)
        
        


    # ── Disk creation :3
    def _MakingTheDisk(self, image=None):
        size =400 
        if image is None:
            img = Image.new("RGBA", (size, size), (40, 40, 50, 255))
        else:
            img = image.resize((size, size), Image.LANCZOS).convert("RGBA")

        # circular crop
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
        img.putalpha(mask)

        # vinyl rings
        draw = ImageDraw.Draw(img, "RGBA")
        cx = cy = size // 2
        for radius in range(cx - 10, 10, -30):
            draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius],
                         outline=(0, 0, 0, 40), width=2)

        # center hole
        r = 16
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(15, 15, 15, 255))

        # shiny center ring
        draw.ellipse([cx-r-3, cy-r-3, cx+r+3, cy+r+3],
                     outline=(80, 80, 80, 180), width=2)
        return img

    # ── Album art + color
    def _gotta_lookcool(self, filepath):
        try:
            tags = ID3(filepath)
            for tag in tags.values():
                if isinstance(tag, APIC):
                    return Image.open(io.BytesIO(tag.data)).convert("RGBA")
        except Exception as e:
            print("art error:", e)
        return None

    def _get_dominant_color(self, image):
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="PNG")
        buf.seek(0)
        return ColorThief(buf).get_color(quality=1)

    # ── Playback 
    def _play_index(self, index):
        self.bg_canvas.itemconfigure(self.play_button, text="⏸")
        self.current_index = index
        filepath = self.playlist[index]

        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        art = self._gotta_lookcool(filepath)
        self.disk_image = self._MakingTheDisk(art)
        self.disk_spin  = True
        self.disk_angle = 0.0

        # update track name on canvas
        try:
            tags= ID3(filepath)
            name=str(tags.get("TIT2",Path(filepath).stem))
            artist=str(tags.get("TPE1",""))
        except:
            name = Path(filepath).stem
            artist=""

        self.bg_canvas.itemconfigure(self.title_id, text=name)
        self.bg_canvas.itemconfigure(self.artist_id, text=artist)

        if art:
            dominant = self._get_dominant_color(art)
            self.bg_current = self.bg_target
            self.bg_target  = tuple(max(0, int(c * 0.65)) for c in dominant)
            self.bg_t = 0.0

        self._refresh_playlist_ui()
    
    

    def _wiggleIt(self):
        if self.current_index < 0:
            return
        pos = pygame.mixer.music.get_pos() / 1000
        if pos < 0:
            return
        from mutagen.mp3 import MP3
        duration = MP3(self.playlist[self.current_index]).info.length
        if duration <= 0:
            return

        pct = min(pos / duration, 1.0)
        x1 = self.cx - 220
        x2 = self.cx + 220
        y  = self.cy + 220
        total_width = x2 - x1
        played_x = x1 + int(total_width * pct)

        steps = 80
        amplitude = 12 if self.disk_spin else 0
        self.wave_offset = (self.wave_offset + 0.15) % (2 * math.pi)

        played_points   = []
        unplayed_points = []

        for i in range(steps + 1):
            x = x1 + int(total_width * i / steps)
            if x <= played_x:
                wave_y = y + int(amplitude * math.sin(i * 0.4 + self.wave_offset))
                played_points.extend([x, wave_y])
            else:
                unplayed_points.extend([x, y])

        if len(played_points) >= 4:
            self.bg_canvas.coords(self.wave_played, *played_points)
        if len(unplayed_points) >= 4:
            self.bg_canvas.coords(self.wave_unplayed, *unplayed_points)

        m, s   = divmod(int(pos), 60)
        dm, ds = divmod(int(duration), 60)
        self.bg_canvas.itemconfigure(self.time_text, text=f"{m}:{s:02d} / {dm}:{ds:02d}")

    # ── File loading 
    def _add_files(self):
        files = filedialog.askopenfilenames(title="Select Music Files",
                                            filetypes=[("Audio Files", "*.mp3 *.flac *.m4a")])
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
        self._refresh_playlist_ui()
        self._save_songs()

    def _shuffleForMebaby(self):
        self.shuffle= not self.shuffle
        color="#ffffff" if self.shuffle else "#555555"
        self.bg_canvas.itemconfigure(self.shffle, fill=color)

    def _saythatagain(self):
        self.repeat = (self.repeat+1)%3
        icons= ["↺", "↺", "➀"]
        colors=["#555555","#ffffff","#ffffff"]
        self.bg_canvas.itemconfigure(self.rpt,text=icons[self.repeat],fill =colors[self.repeat])

# —————— playback Manupilation
    def _refresh_playlist_ui(self):
        for widget in self.playlist_frame.winfo_children():
            widget.destroy()
        for i, filepath in enumerate(self.playlist):
            try:
                tags = ID3(filepath)
                name = str(tags.get("TIT2", Path(filepath).stem))
            except:
                name = Path(filepath).stem
            is_current = (i == self.current_index)

            # row frame
            row_frame = ctk.CTkFrame(self.playlist_frame,
                                    fg_color="#2d1054" if is_current else "transparent",
                                    corner_radius=8)
            row_frame.grid(row=i, column=0, sticky="ew", pady=2, padx=4)
            row_frame.grid_columnconfigure(0, weight=1)

            # track name button
            btn = ctk.CTkButton(row_frame, text=name, anchor="w",
                                fg_color="transparent",
                                hover_color="#3d1a6e",
                                text_color="#d4aaff" if is_current else "#cccccc",
                                font=ctk.CTkFont(size=13, weight="bold" if is_current else "normal"),
                                corner_radius=8,
                                command=lambda i=i: self._play_index(i))
            btn.grid(row=0, column=0, sticky="ew")

            # delete button
            del_btn = ctk.CTkButton(row_frame, text="✕", width=28, height=28,
                                    fg_color="transparent",
                                    hover_color="#6e1a1a",
                                    text_color="#888888",
                                    corner_radius=6,
                                    command=lambda i=i: self._delete_track(i))
            del_btn.grid(row=0, column=1, padx=(0, 4))

    def PlayIt(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.disk_spin=False
            self.bg_canvas.itemconfigure(self.play_button, text="▶")
        else:
            pygame.mixer.music.unpause()
            self.disk_spin=True
            self.bg_canvas.itemconfigure(self.play_button, text="⏸")

    def _next(self):
        if not self.playlist:
            return
        if self.repeat == 2:
            self._play_index(self.current_index)
        elif self.shuffle: 
            import random
            self._play_index(random.randint(0,len(self.playlist)-1))
        else:
            self._play_index((self.current_index+1)%len(self.playlist))

    def _volume(self,val):
        pygame.mixer.music.set_volume(float(val))

    def _prev(self):
        if not self.playlist:
            return
        self._play_index((self.current_index - 1) % len(self.playlist))
#—————Json file handling
    def _save_songs(self):
        with open (self.save_file,"w") as f:
            json.dump(self.playlist,f)
    
    def _load_songs(self):
        print("looking for:", self.save_file.absolute())
        if self.save_file.exists():
            print("file found")
            with open(self.save_file,"r") as f:
                self.playlist = json.load(f)
            print("loaded tracks:", len(self.playlist))
            self._refresh_playlist_ui()
        else:
            print("no save file found")
#Finding something new :)
    def _sail_the_seas(self):
        self.last_query = self.search.get().strip()
        if not self.last_query:
            return
        
        self.search.configure(state="disabled",placeholder_text="Downloading...")
        import threading
        threading.Thread(target=self._download_track, args=(self.last_query,), daemon=True).start()

    def _download_track(self, query):
        import yt_dlp
        download_folder = Path("downloads")
        download_folder.mkdir(exist_ok=True)
        opts = {
            "ffmpeg_location": r"C:\Users\srija\Downloads\ffmpeg-master-latest-win64-gpl\ffmpeg-master-latest-win64-gpl\bin",
            "format": "bestaudio/best",
            "outtmpl": str(download_folder / "%(title)s.%(ext)s"),
            "quiet": True,
            "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                {"key": "EmbedThumbnail"},
            ],
            "writethumbnail": True,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android"],
                }
            },
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                entry = info["entries"][0]
                filepath = ydl.prepare_filename(entry).rsplit(".", 1)[0] + ".mp3"
                self.after(0, self._download_done, filepath)
        except Exception as e:
            print("download error:", e)
            self.after(0, self._reset_search)

    def _download_done(self, filepath):
        if filepath not in self.playlist:
            self.playlist.append(filepath)
            self._save_songs()
            self._refresh_playlist_ui()
        self.search.configure(state="normal",placeholder_text="Search Songs")
        self.search.delete(0,"end")
        self.search.focus_set()

        query=filepath.split("\\")[-1].replace(".mp3","")
        import threading
        threading.Thread(target=self._fixNplay,
                         args=(filepath,self.last_query),daemon=True).start()
        
    def _fixNplay(self,filepath,query):
        self._Unchud_it(filepath,query)
        self.after(0,self._play_index,self.playlist.index(filepath))

    def _reset_search(self):
        self.search.configure(state="normal",placeholder_text="Search Songs")
        self.search.delete(0,"end")
        self.search.focus_set()

    def _Unchud_it(self, filepath, query):
        import requests
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC

        try:
            # iTunes search API — great for Indian music
            r = requests.get("https://itunes.apple.com/search",
                            params={"term": query, "media": "music", "limit": 1},
                            timeout=8)
            results = r.json().get("results", [])
            if not results:
                print("no iTunes results for:", query)
                return

            track     = results[0]
            title     = track.get("trackName", query)
            artist    = track.get("artistName", "")
            album     = track.get("collectionName", "")
            art_url   = track.get("artworkUrl100", "").replace("100x100", "600x600")

            art_data = None
            if art_url:
                img_r = requests.get(art_url, timeout=8)
                if img_r.status_code == 200:
                    art_data = img_r.content

            tags = ID3(filepath)
            tags["TIT2"] = TIT2(encoding=3, text=title)
            tags["TPE1"] = TPE1(encoding=3, text=artist)
            tags["TALB"] = TALB(encoding=3, text=album)
            if art_data:
                tags["APIC:"] = APIC(encoding=3, mime="image/jpeg",
                                    type=3, desc="Cover", data=art_data)
            tags.save()
            print(f"metadata fixed: {title} - {artist}")

        except Exception as e:
            print("metadata error:", e)
   
   
    def _delete_track(self, index):
        if index == self.current_index:
            pygame.mixer.music.stop()
            self.disk_spin = False
            self.current_index = -1
            self.disk_image = None
        elif index < self.current_index:
            self.current_index -= 1
        
        self.playlist.pop(index)
        self._save_songs()
        self._refresh_playlist_ui()


app = MusicPlayer()
app.mainloop()