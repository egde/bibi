from typing import Optional
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Select, Input, Footer, Markdown
from textual.containers import ScrollableContainer, Container
from textual.widget import Widget
from bs4 import BeautifulSoup as bs 
import json
import requests

HTTP_METHODS = [
    "GET",
    "POST",
    "PUT",
    "DELETE"
]

async def send_request(
        url:str, 
        body:Optional[any] = None, 
        method: str = "GET") -> requests.Response:
    
    response = None
    match method:
        case "POST":
            response = requests.post(url=url, data=body)
        case _:
            response = requests.get(url=url)
    return response

    
        

class RequestComponent(Static):
    method: str = 'GET'
    url: str

    @on(Select.Changed)
    def on_method_selected(self, event: Select.Changed) -> None:
        self.method = str(event.value)

    @on(Input.Changed)
    def on_url_changed(self, event: Input.Changed) -> None:
        self.url = str(event.value)


    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == 'btnSend':
            async def _send_request():
                response = await send_request(method=self.method, url=self.url)
                app.query_one('#cmpResponse').update(response)

            self.run_worker(_send_request(), exclusive=True)

    def compose(self) -> ComposeResult:
        yield Container(
            Select(options=[(method, method) for method in HTTP_METHODS], value="GET",id="sltMethod"), 
            Input(placeholder="URL", id='txtUrl'),
            id="input")
        yield Container(
            Button("Send", id="btnSend", variant="success"),
            Button("Save", id="btnSave"),
            id="buttons")

class ResponseComponent(Static):
    def update(self, response: requests.Response):
        content_type = response.headers.get('Content-Type')
        if 'html' in content_type:
            soup = bs(response.text)
            content = soup.prettify()
        elif 'json' in content_type:
            content = json.dumps(response.json(), indent=2)
        else:
            content = response.text
        
        headers = ["| "+header+" | "+value+ " |" for header, value in response.headers.items()]
        headers_str = '\n'.join(headers)
        md = f"""
# Headers

| Header       | Value                  |
|--------------|------------------------|
|Response Code | {response.status_code} |
{headers_str}

# Body
```
{content}
```

# Statistics
"""


        self.query_one('#mdResponse').update(md)
        
    
    def compose(self):
        yield ScrollableContainer(Markdown(id = 'mdResponse', markdown="** No Response **"))


class BibiApp(App):
    CSS_PATH = "bibi.css"

    BINDINGS = [("q", "quit", "Quit bibi")]

    def compose(self) -> ComposeResult:
        yield RequestComponent(id="cmpRequest")
        yield ResponseComponent(id="cmpResponse")
        yield Footer()
    
    def quit(self):
        app.exit()

if __name__ == "__main__":
    app = BibiApp()
    app.run()