from markupsafe import Markup

class UICreator:
    HTML = ""
    
    def Header(self, h_type, h_text):
        self.HTML += Markup(
            f"""
                <h{h_type} class="mx-auto text-center w-75" style="margin-top: 25px; border: 3px solid white; border-radius: 25px;">
                    {h_text}
                </h{h_type}>
            """
        )