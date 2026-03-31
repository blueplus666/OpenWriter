# main.py
# -*- coding: utf-8 -*-
import logging
import customtkinter as ctk
from ui import NovelGeneratorGUI
from theme.theme_manager import get_theme_manager
from utils import get_persistence_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    # 初始化主题管理器
    theme_mgr = get_theme_manager()

    # 初始化持久性存储管理器
    persistence = get_persistence_manager()

    # 创建主窗口
    app = ctk.CTk()

    # 设置窗口标题
    app.title("OpenWriter")

    # 设置窗口图标
    import os

    try:
        if os.path.exists("icon.ico"):
            app.iconbitmap("icon.ico")
    except Exception:
        pass

    # 从持久性存储加载主题
    saved_theme = persistence.get("theme", "theme_name")
    saved_mode = persistence.get("theme", "color_mode")
    if saved_theme:
        theme_mgr.load_theme(saved_theme, saved_mode or "light")

    # 设置窗口大小
    saved_width = persistence.get("window", "width") or 1400
    saved_height = persistence.get("window", "height") or 900
    app.geometry(f"{saved_width}x{saved_height}")
    app.minsize(1200, 700)

    # 创建GUI
    gui = NovelGeneratorGUI(app)

    # 窗口关闭时保存配置
    def on_closing():
        try:
            # 保存窗口大小
            persistence.update_window_size(app.winfo_width(), app.winfo_height())
            # 保存所有配置
            gui.save_all_configurations()
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
        finally:
            app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # 运行主循环
    app.mainloop()


if __name__ == "__main__":
    main()