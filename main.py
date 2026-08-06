from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.metrics import dp

from plyer import filechooser, share

from opl_template import generate_pdf


class OPLForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(15), size_hint_y=None, **kwargs)
        self.bind(minimum_height=self.setter("height"))

        self.no_good_path = None
        self.good_path = None
        self.classification = None

        # --- Photos ---
        self.add_widget(Label(text="Photos", bold=True, size_hint_y=None, height=dp(30), font_size=dp(18)))

        photo_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(70))
        self.no_good_btn = Button(text="📷 No Good Photo", font_size=dp(16))
        self.no_good_btn.bind(on_release=lambda x: self.pick_photo("no_good"))
        self.good_btn = Button(text="📷 Good Photo", font_size=dp(16))
        self.good_btn.bind(on_release=lambda x: self.pick_photo("good"))
        photo_row.add_widget(self.no_good_btn)
        photo_row.add_widget(self.good_btn)
        self.add_widget(photo_row)

        # --- Information ---
        self.add_widget(Label(text="Information", bold=True, size_hint_y=None, height=dp(30), font_size=dp(18)))

        self.theme_input = TextInput(hint_text="Theme", size_hint_y=None, height=dp(50), multiline=False)
        self.add_widget(self.theme_input)

        self.prepared_by_input = TextInput(hint_text="Prepared By", size_hint_y=None, height=dp(50), multiline=False)
        self.add_widget(self.prepared_by_input)

        # --- Classification ---
        self.add_widget(Label(text="Classification", bold=True, size_hint_y=None, height=dp(30), font_size=dp(18)))

        class_options = ["Basic Knowledge", "Improvement Cases", "Troubleshooting Cases"]
        self.class_checks = {}
        for opt in class_options:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
            cb = CheckBox(group="classification", size_hint_x=None, width=dp(40))
            cb.bind(active=lambda cb_inst, value, name=opt: self.set_classification(name, value))
            row.add_widget(cb)
            row.add_widget(Label(text=opt, halign="left"))
            self.class_checks[opt] = cb
            self.add_widget(row)

        # --- Highlight / Learning ---
        self.add_widget(Label(text="Highlight / Learning", bold=True, size_hint_y=None, height=dp(30), font_size=dp(18)))
        self.highlight_input = TextInput(hint_text="Enter details...", size_hint_y=None, height=dp(120), multiline=True)
        self.add_widget(self.highlight_input)

        # --- PQCDSM ---
        self.add_widget(Label(text="PQCDSM", bold=True, size_hint_y=None, height=dp(30), font_size=dp(18)))
        self.pqcdsm_checks = {}
        pqcdsm_grid = GridLayout(cols=3, size_hint_y=None, height=dp(100))
        for letter in ["P", "Q", "C", "D", "S", "M"]:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
            cb = CheckBox(size_hint_x=None, width=dp(40))
            self.pqcdsm_checks[letter] = cb
            row.add_widget(cb)
            row.add_widget(Label(text=letter))
            pqcdsm_grid.add_widget(row)
        self.add_widget(pqcdsm_grid)

        # --- Share Button ---
        self.share_btn = Button(text="📤 Share OPL", size_hint_y=None, height=dp(70), font_size=dp(20), bold=True)
        self.share_btn.bind(on_release=lambda x: self.on_share())
        self.add_widget(self.share_btn)

    def set_classification(self, name, value):
        if value:
            self.classification = name

    def pick_photo(self, which):
        filechooser.open_file(
            on_selection=lambda selection: self.on_photo_selected(which, selection),
            filters=["*.jpg", "*.jpeg", "*.png"],
        )

    def on_photo_selected(self, which, selection):
        if not selection:
            return
        path = selection[0]
        if which == "no_good":
            self.no_good_path = path
            self.no_good_btn.text = "✅ No Good Photo Selected"
        else:
            self.good_path = path
            self.good_btn.text = "✅ Good Photo Selected"

    def show_error(self, message):
        popup = Popup(title="Missing Information", content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

    def on_share(self):
        theme = self.theme_input.text.strip()
        prepared_by = self.prepared_by_input.text.strip()

        if not theme:
            self.show_error("Please enter a Theme.")
            return
        if not prepared_by:
            self.show_error("Please enter Prepared By.")
            return
        if not self.classification:
            self.show_error("Please select a Classification.")
            return
        if not self.no_good_path or not self.good_path:
            self.show_error("Please select both photos.")
            return

        pqcdsm_selected = [letter for letter, cb in self.pqcdsm_checks.items() if cb.active]

        data = {
            "theme": theme,
            "prepared_by": prepared_by,
            "classification": self.classification,
            "highlight": self.highlight_input.text.strip(),
            "pqcdsm": pqcdsm_selected,
            "no_good_photo": self.no_good_path,
            "good_photo": self.good_path,
        }

        pdf_path = generate_pdf(data)

        share.share(
            title="Share OPL",
            text="OPL PDF",
            filepath=pdf_path,
            mimetype="application/pdf",
        )


class OPLApp(App):
    def build(self):
        scroll = ScrollView()
        scroll.add_widget(OPLForm())
        return scroll


if __name__ == "__main__":
    OPLApp().run()
