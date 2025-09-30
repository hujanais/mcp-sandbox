import os
import webbrowser

class WebBrowserTools():
    """Tools for opening a page on the web browser"""

    def __init__(self):
        pass

    def open_page(self, url: str, new_window: bool = False):
        """Open a URL in a browser window
        Args:
            url (str): URL to open
            new_window (bool): If True, open in a new window, otherwise open in a new tab. Default is False.
        Returns:
            None
        """
        if new_window:
            webbrowser.open_new(url)
        else:
            webbrowser.open_new_tab(url)

if __name__ == "__main__":
    tool = WebBrowserTools()
    root = os.getcwd()
    url =  'file://' + root + '/chart.html'
    tool.open_page(url)