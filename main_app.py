from __future__ import annotations
import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Set

try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

from library_models import LibraryPhoto
from library_store import LibraryStore
from import_service import import_files
from tag_parser import parse as parse_tags
from app_settings import AppSettings, FocalMode


def _trim_number(x: float) -> str:
    s = f"{x:.2f}"
    if s.endswith(".00"):
        return s[:-3]
    if s.endswith("0"):
        return s[:-1]
    return s


def _shutter_text(seconds: float) -> str:
    if seconds >= 1.0:
        return f"{_trim_number(seconds)} s"
    denom = max(1, round(1.0 / seconds))
    return f"1/{denom} s"


def _load_tk_image(path: str, max_pixel: int = 150) -> Optional["ImageTk.PhotoImage"]:
    if not _PIL_OK or not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        img.thumbnail((max_pixel, max_pixel), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class PhotoDetailWindow(tk.Toplevel):
    def __init__(self, parent, photo: LibraryPhoto, settings: AppSettings):
        super().__init__(parent)
        self.title(photo.file_name)
        self.resizable(True, True)
        self.minsize(640, 520)
        self._photo = photo
        self._settings = settings
        self._tk_img = None
        self._build_ui()
        self.lift()
        self.focus_force()

    def _build_ui(self):
        p = self._photo
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=p.file_name, font=("", 13, "bold"),
                  wraplength=600, justify="left").pack(anchor="w")

        img_frame = ttk.Frame(frame, relief="flat")
        img_frame.pack(fill=tk.X, pady=(6, 0))
        self._img_label = ttk.Label(img_frame, background="#ebebeb")
        self._img_label.pack(fill=tk.X)
        self._load_image()

        canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=8)

        self._build_info(scroll_frame)

    def _load_image(self):
        if _PIL_OK and self._photo.thumbnail_path:
            try:
                img = Image.open(self._photo.thumbnail_path)
                img.thumbnail((600, 400), Image.LANCZOS)
                self._tk_img = ImageTk.PhotoImage(img)
                self._img_label.configure(image=self._tk_img)
                return
            except Exception:
                pass
        self._img_label.configure(text="[无法加载图片]", anchor="center")

    def _build_info(self, parent):
        p = self._photo

        basic = ttk.LabelFrame(parent, text="基本信息", padding=8)
        basic.pack(fill=tk.X, padx=4, pady=4)

        if p.capture_date:
            self._row(basic, "拍摄时间", p.capture_date.strftime("%Y-%m-%d %H:%M"))
        self._row(basic, "文件路径", p.source_path, selectable=True)
        self._row(basic, "导入时间", p.import_date.strftime("%Y-%m-%d %H:%M"))

        ttk.Separator(basic, orient="horizontal").pack(fill=tk.X, pady=4)

        ttk.Button(
            basic, text="在 Finder 中显示原图",
            command=lambda: subprocess.run(["open", "-R", p.source_path])
        ).pack(anchor="w")

        exif_frame = ttk.LabelFrame(parent, text="拍摄参数", padding=8)
        exif_frame.pack(fill=tk.X, padx=4, pady=4)

        if p.exif:
            e = p.exif
            if e.camera_model:
                self._row(exif_frame, "机身", e.camera_model)
            if e.lens_model:
                self._row(exif_frame, "镜头", e.lens_model)
            if e.f_number is not None:
                self._row(exif_frame, "光圈", f"f/{_trim_number(e.f_number)}")
            if e.exposure_time is not None:
                self._row(exif_frame, "快门", _shutter_text(e.exposure_time))
            if e.iso is not None:
                self._row(exif_frame, "ISO", str(e.iso))
            if e.focal_length is not None:
                mul = self._settings.focal_multiplier(e.camera_model)
                shown = e.focal_length * mul
                suffix = " mm（等效）" if mul == 1.5 else " mm"
                self._row(exif_frame, "焦距", f"{_trim_number(shown)}{suffix}")

    def _row(self, parent, key: str, value: str, selectable: bool = False):
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=f"{key}：", width=10,
                  foreground="gray", anchor="e").pack(side=tk.LEFT)
        if selectable:
            entry = ttk.Entry(row)
            entry.insert(0, value)
            entry.configure(state="readonly")
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            ttk.Label(row, text=value, wraplength=450, justify="left",
                      anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, settings: AppSettings):
        super().__init__(parent)
        self.title("设置")
        self.resizable(False, False)
        self._settings = settings
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="焦距显示：").grid(row=0, column=0, sticky="e", padx=(0, 8))

        self._mode_var = tk.StringVar(value=self._settings.focal_mode.title)
        cb = ttk.Combobox(
            frame,
            textvariable=self._mode_var,
            values=[m.title for m in FocalMode],
            width=24,
            state="readonly",
        )
        cb.grid(row=0, column=1, sticky="w")

        def on_change(event=None):
            selected_title = self._mode_var.get()
            for m in FocalMode:
                if m.title == selected_title:
                    self._settings.focal_mode = m
                    break

        cb.bind("<<ComboboxSelected>>", on_change)

        ttk.Button(frame, text="关闭", command=self.destroy).grid(
            row=1, column=0, columnspan=2, pady=(12, 0)
        )


class TaggerApp(tk.Tk):
    _THUMB_SIZE = 150

    def __init__(self):
        super().__init__()
        self.title("TAGGER")
        self.minsize(900, 600)
        self._store = LibraryStore()
        self._settings = AppSettings()
        self._selected_ids: Set[str] = set()
        self._current_tag: Optional[str] = None
        self._thumb_cache: dict = {}

        self._store.add_listener(self._refresh)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        toolbar = ttk.Frame(self, padding=(8, 4))
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(toolbar, text="导入…", command=self._import_files).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="设置", command=self._open_settings).pack(side=tk.LEFT, padx=4)

        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        sidebar_frame = ttk.Frame(pane, width=180)
        pane.add(sidebar_frame, weight=0)

        ttk.Label(sidebar_frame, text="TAGGER", font=("", 13, "bold"),
                  padding=(8, 6)).pack(anchor="w")

        self._sidebar_list = tk.Listbox(sidebar_frame, selectmode=tk.SINGLE,
                                        activestyle="none", relief="flat",
                                        highlightthickness=0)
        self._sidebar_list.pack(fill=tk.BOTH, expand=True)
        self._sidebar_list.bind("<<ListboxSelect>>", self._on_sidebar_select)
        self._sidebar_list.bind("<Button-2>", self._sidebar_context_menu)
        self._sidebar_list.bind("<Button-3>", self._sidebar_context_menu)

        right = ttk.Frame(pane)
        pane.add(right, weight=1)

        header = ttk.Frame(right, padding=(8, 4))
        header.pack(fill=tk.X)
        self._title_var = tk.StringVar()
        self._count_var = tk.StringVar()
        ttk.Label(header, textvariable=self._title_var,
                  font=("", 12, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, textvariable=self._count_var,
                  foreground="gray").pack(side=tk.LEFT, padx=8)
        ttk.Button(header, text="删除选中",
                   command=self._delete_selected).pack(side=tk.RIGHT)

        tag_bar = ttk.LabelFrame(right, text="给选中照片添加标签", padding=8)
        tag_bar.pack(fill=tk.X, padx=8, pady=4)
        tag_inner = ttk.Frame(tag_bar)
        tag_inner.pack(fill=tk.X)
        self._tag_input = tk.StringVar()
        ttk.Entry(tag_inner, textvariable=self._tag_input).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(tag_inner, text="添加", command=self._add_tags).pack(
            side=tk.LEFT, padx=(6, 0))
        self._selected_count_var = tk.StringVar(value="已选 0 张")
        ttk.Label(tag_bar, textvariable=self._selected_count_var,
                  foreground="gray").pack(anchor="e")

        grid_container = ttk.Frame(right)
        grid_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._canvas = tk.Canvas(grid_container, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(grid_container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = ttk.Frame(self._canvas)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw"
        )
        self._grid_frame.bind("<Configure>", self._on_grid_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _refresh(self):
        self._refresh_sidebar()
        self._refresh_grid()

    def _refresh_sidebar(self):
        lb = self._sidebar_list
        old_sel = lb.curselection()
        old_idx = old_sel[0] if old_sel else 0

        lb.delete(0, tk.END)
        self._sidebar_items = []

        untagged_count = len(self._store.untagged_photos())
        lb.insert(tk.END, f"  未标签  ({untagged_count})")
        self._sidebar_items.append(None)

        for ts in self._store.tags():
            lb.insert(tk.END, f"  #{ts.tag}  ({ts.count})")
            self._sidebar_items.append(ts.tag)

        target = min(old_idx, lb.size() - 1)
        lb.selection_set(target)
        lb.see(target)

        if target < len(self._sidebar_items):
            self._current_tag = self._sidebar_items[target]

    def _refresh_grid(self):
        for w in self._grid_frame.winfo_children():
            w.destroy()

        photos = (self._store.untagged_photos() if self._current_tag is None
                  else self._store.photos_for_tag(self._current_tag))

        title = "未标签" if self._current_tag is None else f"#{self._current_tag}"
        self._title_var.set(title)
        self._count_var.set(f"{len(photos)} 张")

        canvas_width = self._canvas.winfo_width()
        cols = max(1, canvas_width // (self._THUMB_SIZE + 16))

        for idx, photo in enumerate(photos):
            row, col = divmod(idx, cols)
            card = self._make_card(photo)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        self._update_selected_count()

    def _make_card(self, photo: LibraryPhoto) -> tk.Frame:
        is_selected = photo.id in self._selected_ids
        bg = "#cce0ff" if is_selected else "#f5f5f5"

        card = tk.Frame(self._grid_frame, bg=bg, bd=1,
                        relief="solid", cursor="hand2",
                        width=self._THUMB_SIZE + 16,
                        height=self._THUMB_SIZE + 60)
        card.pack_propagate(False)

        tk_img = self._get_thumb(photo.thumbnail_path)
        if tk_img:
            img_label = tk.Label(card, image=tk_img, bg=bg, cursor="hand2")
            img_label.image = tk_img
        else:
            img_label = tk.Label(card, text="📷", bg=bg, font=("", 32))
        img_label.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text=photo.file_name, bg=bg,
                 font=("", 9), wraplength=self._THUMB_SIZE,
                 justify="left", anchor="w").pack(fill=tk.X, padx=4)

        date_str = (photo.capture_date or photo.import_date).strftime("%Y-%m-%d")
        tk.Label(card, text=date_str, bg=bg,
                 font=("", 8), foreground="gray").pack(anchor="w", padx=4)

        # 单击 / 双击 区分
        click_timer = [None]

        def on_click(e, pid=photo.id):
            if click_timer[0] is not None:
                self.after_cancel(click_timer[0])
            click_timer[0] = self.after(250, lambda: self._toggle_select(pid))

        def on_dbl_click(e, p=photo):
            if click_timer[0] is not None:
                self.after_cancel(click_timer[0])
                click_timer[0] = None
            self._open_detail(p)

        for widget in [card, img_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_dbl_click)

        # 右键菜单
        def show_ctx(e, p=photo):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label="删除这张照片（仅从库移除）",
                command=lambda: self._confirm_delete({p.id})
            )
            if self._selected_ids:
                menu.add_command(
                    label="删除已选照片（仅从库移除）",
                    command=lambda: self._confirm_delete(set(self._selected_ids))
                )
            menu.tk_popup(e.x_root, e.y_root)

        card.bind("<Button-2>", show_ctx)
        card.bind("<Button-3>", show_ctx)

        return card

    def _get_thumb(self, path: Optional[str]) -> Optional["ImageTk.PhotoImage"]:
        if not path:
            return None
        if path not in self._thumb_cache:
            self._thumb_cache[path] = _load_tk_image(path, self._THUMB_SIZE)
        return self._thumb_cache[path]

    def _on_sidebar_select(self, event=None):
        sel = self._sidebar_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self._sidebar_items):
            self._current_tag = self._sidebar_items[idx]
        self._selected_ids.clear()
        self._refresh_grid()

    def _sidebar_context_menu(self, event):
        idx = self._sidebar_list.nearest(event.y)
        if idx < 0 or idx >= len(self._sidebar_items):
            return
        tag = self._sidebar_items[idx]
        if tag is None:
            return
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label=f"删除标签「{tag}」（从所有照片移除）",
            command=lambda: self._delete_tag(tag)
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _toggle_select(self, photo_id: str):
        if photo_id in self._selected_ids:
            self._selected_ids.discard(photo_id)
        else:
            self._selected_ids.add(photo_id)
        self._refresh_grid()

    def _open_detail(self, photo: LibraryPhoto):
        win = PhotoDetailWindow(self, photo, self._settings)
        win.lift()
        win.focus_force()

    def _open_settings(self):
        SettingsWindow(self, self._settings)

    def _import_files(self):
        paths = filedialog.askopenfilenames(
            title="导入照片",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.tiff *.tif *.heic *.raw *.arw *.cr2 *.nef"),
                ("所有文件", "*.*")
            ]
        )
        if not paths:
            return
        result = import_files(list(paths), initial_tags=[])
        for p in result.imported:
            self._store.add_imported(p)
        self._current_tag = None
        self._refresh()
        if result.failures:
            names = "\n".join(os.path.basename(f) for f, _ in result.failures)
            messagebox.showwarning("导入失败", f"以下文件导入失败：\n{names}")

    def _add_tags(self):
        tags = parse_tags(self._tag_input.get())
        if not tags or not self._selected_ids:
            return
        self._store.add_tags(set(self._selected_ids), tags)
        self._tag_input.set("")
        self._selected_ids.clear()
        self._refresh()

    def _delete_tag(self, tag: str):
        if messagebox.askyesno("确认", f"从所有照片移除标签「{tag}」？"):
            self._store.delete_tag_globally(tag)
            if self._current_tag == tag:
                self._current_tag = None
            self._refresh()

    def _delete_selected(self):
        if not self._selected_ids:
            return
        self._confirm_delete(set(self._selected_ids))

    def _confirm_delete(self, ids: set):
        if messagebox.askyesno(
            "确认删除",
            f"将从 TAGGER 索引库中移除 {len(ids)} 张照片（不会删除原始图片文件）。"
        ):
            self._store.delete_photos(ids, delete_thumbnail_files=True)
            self._selected_ids -= ids
            self._refresh()

    def _update_selected_count(self):
        self._selected_count_var.set(f"已选 {len(self._selected_ids)} 张")

    def _on_grid_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self._canvas.itemconfig(self._canvas_window, width=event.width)
        self._refresh_grid()

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * event.delta / 120), "units")


if __name__ == "__main__":
    app = TaggerApp()
    app.lift()
    app.attributes("-topmost", True)
    app.after(200, lambda: app.attributes("-topmost", False))
    app.focus_force()
    app.mainloop()
