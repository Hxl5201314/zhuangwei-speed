from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import mainthread
import threading
import time
from datetime import datetime
from ping3 import ping

class MainLayout(BoxLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 6
        self.padding = 10
        self.is_running = False

        self.acc_input = TextInput(hint_text="209装维账号", size_hint_y=None, height=44)
        self.pwd_input = TextInput(hint_text="密码", password=True, size_hint_y=None, height=44)
        self.ip_input = TextInput(hint_text="光猫管理IP", text="192.168.1.1", size_hint_y=None, height=44)
        self.ping_ip = TextInput(hint_text="测速目标IP", text="223.5.5.5", size_hint_y=None, height=44)
        self.ping_count = TextInput(hint_text="ping次数", text="20", size_hint_y=None, height=44)

        self.add_widget(self.acc_input)
        self.add_widget(self.pwd_input)
        self.add_widget(self.ip_input)
        self.add_widget(self.ping_ip)
        self.add_widget(self.ping_count)

        btn_box = BoxLayout(spacing=8, size_hint_y=None, height=44)
        self.btn_start = Button(text="开始测速")
        self.btn_start.bind(on_press=self.start_test)
        self.btn_stop = Button(text="停止")
        self.btn_stop.bind(on_press=self.stop_test)
        btn_box.add_widget(self.btn_start)
        btn_box.add_widget(self.btn_stop)
        self.add_widget(btn_box)

        scroll = ScrollView()
        self.log_text = TextInput(readonly=True)
        scroll.add_widget(self.log_text)
        self.add_widget(scroll)

    @mainthread
    def add_log(self, txt):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.text += f"[{t}] {txt}\n"

    def start_test(self, *args):
        if self.is_running:
            return
        acc = self.acc_input.text.strip()
        pwd = self.pwd_input.text.strip()
        if not acc or not pwd:
            self.add_log("⚠️ 请填写209账号和密码！")
            return
        self.is_running = True
        self.add_log("==== Ping测速开始（ping3） ====")
        th = threading.Thread(target=self.run_ping_test, daemon=True)
        th.start()

    def stop_test(self, *args):
        self.is_running = False
        self.add_log("✅ 用户手动停止测试")

    def run_ping_test(self):
        target = self.ping_ip.text.strip()
        try:
            count = int(self.ping_count.text.strip())
        except ValueError:
            self.add_log("❌ ping次数输入错误")
            self.is_running = False
            return
        ok = 0
        total_delay = 0.0
        for i in range(count):
            if not self.is_running:
                break
            delay = ping(target, timeout=1)
            if delay is not None:
                delay_ms = delay * 1000
                ok += 1
                total_delay += delay_ms
                self.add_log(f"第{i+1}次 成功，延迟 {delay_ms:.2f} ms")
            else:
                self.add_log(f"第{i+1}次 请求超时")
            time.sleep(1)
        if ok > 0:
            avg = total_delay / ok
            self.add_log(f"==== 测试完成：成功{ok}/{count}，平均延迟 {avg:.2f} ms ====")
        else:
            self.add_log("==== 全部测试失败 ====")
        self.is_running = False

class SpeedApp(App):
    def build(self):
        self.title = "装维209测速工具"
        return MainLayout()

if __name__ == "__main__":
    SpeedApp().run()
