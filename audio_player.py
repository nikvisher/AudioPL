import tkinter as tk
from tkinter import ttk, filedialog
from pygame import mixer
from mutagen.mp3 import MP3
import threading
import time


class AudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("AduioPL")
        self.root.geometry("700x500+600+300")
        self.root.update_idletasks()
        self.root.configure(bg="#2e2e2e")
        self.root.resizable(False, False)


        # Установка иконки
        try:
            self.icon_image = tk.PhotoImage(file="logo.png")  # Измените на путь к вашему файлу
            self.root.iconphoto(False, self.icon_image)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")

        # Инициализация mixer
        mixer.init()

        # Переменные
        self.playlist = []
        self.current_track_index = -1
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0  # Для отслеживания текущей позиции при паузе

        # Список плейлиста
        self.playlist_box = tk.Listbox(root, selectmode=tk.SINGLE, font=("Arial", 12), bg="#3c3c3c", fg="white", selectbackground="gray")
        self.playlist_box.pack(pady=20, fill=tk.BOTH, expand=True)

        # Кнопки добавления/удаления
        controls_frame = tk.Frame(root, bg="#2e2e2e")
        controls_frame.pack(pady=10)

        self.add_button = ttk.Button(controls_frame, text="Добавить в плейлист", command=self.add_to_playlist)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = ttk.Button(controls_frame, text="Удалить из плейлиста", command=self.remove_from_playlist)
        self.remove_button.pack(side=tk.LEFT, padx=5)

        # Кнопки управления воспроизведением
        play_controls_frame = tk.Frame(root, bg="#2e2e2e")
        play_controls_frame.pack(pady=10)

        self.play_button = ttk.Button(play_controls_frame, text="▶️ Играть", command=self.play_audio)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = ttk.Button(play_controls_frame, text="⏸️ Пауза", command=self.pause_audio)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(play_controls_frame, text="⏹️ Стоп", command=self.stop_audio)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.prev_button = ttk.Button(play_controls_frame, text="⏪ Назад", command=self.prev_track)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(play_controls_frame, text="⏩ Вперед", command=self.next_track)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # Управление громкостью
        volume_frame = tk.Frame(root, bg="#2e2e2e")
        volume_frame.pack(pady=10)

        self.volume_label = tk.Label(volume_frame, text="Громкость", font=("Arial", 12), fg="white", bg="#2e2e2e")
        self.volume_label.pack(side=tk.LEFT, padx=5)

        self.volume_scale = tk.Scale(volume_frame, from_=0, to=1, resolution=0.01, orient="horizontal", command=self.set_volume, bg="#3c3c3c", fg="white")
        self.volume_scale.set(0.5)  # Начальная громкость 50%
        self.volume_scale.pack(side=tk.LEFT)

        # Индикатор прогресса
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Длительность
        self.duration_label = tk.Label(root, text="00:00 / 00:00", font=("Arial", 12), fg="white", bg="#2e2e2e")
        self.duration_label.pack()

    def add_to_playlist(self):
        files = filedialog.askopenfilenames(filetypes=[("Аудиофайлы", "*.mp3 *.wav *.ogg *.flac")])
        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                self.playlist_box.insert(tk.END, file.split("/")[-1])

    def remove_from_playlist(self):
        selected = self.playlist_box.curselection()
        if selected:
            index = selected[0]
            self.playlist_box.delete(index)
            self.playlist.pop(index)
            self.stop_audio()  # Сброс всех настроек при удалении трека

    def play_audio(self):
        if self.is_paused:
            # Продолжить воспроизведение с текущей позиции
            mixer.music.unpause()
            self.is_playing = True
            self.is_paused = False
        else:
            selected = self.playlist_box.curselection()
            if selected:
                self.current_track_index = selected[0]
                self.load_and_play_track(self.current_track_index)

    def pause_audio(self):
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
            self.is_paused = True

    def stop_audio(self):
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0  # Сброс позиции

    def prev_track(self):
        if self.current_track_index > 0:
            self.load_and_play_track(self.current_track_index - 1)

    def next_track(self):
        if self.current_track_index < len(self.playlist) - 1:
            self.load_and_play_track(self.current_track_index + 1)

    def load_and_play_track(self, index):
        self.stop_audio()
        self.current_track_index = index
        track_path = self.playlist[self.current_track_index]
        mixer.music.load(track_path)
        mixer.music.play()
        self.is_playing = True
        self.is_paused = False

        self.playlist_box.selection_clear(0, tk.END)  # Снять выделение со всех элементов
        self.playlist_box.selection_set(self.current_track_index)  # Выделить текущий трек
        self.playlist_box.activate(self.current_track_index)  # Сделать текущий трек активным

        self.update_progress_bar()

    def set_volume(self, value):
        # Установка громкости
        volume = float(value)
        mixer.music.set_volume(volume)

    def update_progress_bar(self):
        def update():
            while self.is_playing:
                current_time = mixer.music.get_pos() / 1000  # Получаем текущее время в секундах
                track_length = self.get_track_length(self.playlist[self.current_track_index])
                progress = (current_time / track_length) * 100
                self.progress_bar["value"] = progress
                minutes, seconds = divmod(int(current_time), 60)
                self.duration_label.config(text=f"{minutes:02d}:{seconds:02d} / {self.get_track_duration(self.current_track_index)}")
                time.sleep(1)
        
        threading.Thread(target=update, daemon=True).start()

    def get_track_length(self, track_path):
        try:
            audio = MP3(track_path)
            return int(audio.info.length)
        except Exception:
            return 0  # Возврат 0, если не удалось получить длительность трека

    def get_track_duration(self, index):
        track_path = self.playlist[index]
        length = self.get_track_length(track_path)
        minutes, seconds = divmod(length, 60)
        return f"{minutes:02d}:{seconds:02d}"


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPlayer(root)
    root.mainloop()
