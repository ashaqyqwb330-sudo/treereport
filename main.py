# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore
import os
from openai import OpenAI

# ---------- تخزين المفتاح ----------
store = JsonStore("settings.json")

def get_token():
    if store.exists("github_token"):
        return store.get("github_token")["value"]
    return None

def save_token(token):
    store.put("github_token", value=token)

# ---------- دوال الشجرة والتحليل ----------
def generate_tree(startpath, prefix=""):
    try:
        contents = sorted(os.listdir(startpath))
    except:
        return
    for i, item in enumerate(contents):
        if item.startswith('.'): continue
        path = os.path.join(startpath, item)
        is_last = (i == len(contents)-1)
        connector = "└── " if is_last else "├── "
        yield prefix + connector + item
        if os.path.isdir(path):
            ext = "    " if is_last else "│   "
            yield from generate_tree(path, prefix + ext)

def analyze_tree(tree_text):
    token = get_token()
    if not token:
        return "❌ عيّن مفتاح GitHub أولاً (اضغط طويلاً على زر الإعدادات)"
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"حلل هذه الشجرة بالعربية:\n{tree_text}"}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ فشل الاتصال: {e}"

# ---------- واجهة التطبيق ----------
class TreeApp(App):
    def build(self):
        self.title = "🌳 مولد التقارير الذكي"
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        top_bar = BoxLayout(size_hint=(1, 0.07))
        self.btn_generate = Button(text="🚀 ولّد التقرير", size_hint=(0.7, 1))
        self.btn_generate.bind(on_press=self.generate_report)
        self.btn_settings = Button(text="⚙️", size_hint=(0.3, 1))
        self.btn_settings.bind(on_press=self.open_settings)
        top_bar.add_widget(self.btn_generate)
        top_bar.add_widget(self.btn_settings)
        layout.add_widget(top_bar)

        self.filechooser = FileChooserListView(dirselect=True, size_hint=(1, 0.4))
        layout.add_widget(self.filechooser)

        self.output = TextInput(text="", readonly=True, size_hint=(1, 0.53))
        layout.add_widget(self.output)

        if not get_token():
            self.show_token_popup()
        return layout

    def generate_report(self, instance):
        selected = self.filechooser.selection
        if not selected:
            self.output.text = "⚠️ اختر مجلداً من القائمة أعلاه."
            return
        path = selected[0]
        self.output.text = "⏳ جارٍ إنشاء الشجرة..."
        tree = "\n".join([path] + list(generate_tree(path)))
        self.output.text = "🌳 الشجرة:\n" + tree
        self.output.text += "\n\n🤖 جارٍ تحليل الذكاء الاصطناعي..."
        analysis = analyze_tree(tree)
        self.output.text = "🌳 الشجرة:\n" + tree + "\n\n🤖 تحليل AI:\n" + analysis

    def open_settings(self, instance):
        self.show_token_popup()

    def show_token_popup(self):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text="أدخل GITHUB_TOKEN الخاص بك:"))
        token_input = TextInput(text=get_token() or "", password=True)
        popup_layout.add_widget(token_input)
        btn_save = Button(text="حفظ", size_hint=(1, 0.2))
        popup_layout.add_widget(btn_save)

        popup = Popup(title="إعداد المفتاح", content=popup_layout, size_hint=(0.8, 0.4))
        btn_save.bind(on_press=lambda x: self.save_and_close(token_input.text, popup))
        popup.open()

    def save_and_close(self, token, popup):
        save_token(token)
        popup.dismiss()
        if get_token():
            self.output.text = "✅ تم حفظ المفتاح بنجاح."

if __name__ == '__main__':
    TreeApp().run()
