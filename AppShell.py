class AppShell:
    """
    Owns the flow between App Views inside the single application window.

    The shell deliberately knows nothing about Arcade. It is given a window and
    a table of view builders, and it only ever asks the window to show a view or
    to close. That keeps the flow testable without a graphical display, and it
    is where later tickets register their own App Views.
    """

    def __init__(self, window, view_builders):
        self.window = window
        # name -> function that builds that App View when it is actually needed.
        # Building is delayed because Arcade views cannot exist before a window does.
        self.view_builders = view_builders
        self.current_view_name = None
        self.is_running = False

    def start(self):
        """Open the app on the Menu App View."""
        self.is_running = True
        self.show_view("menu")

    def register_view(self, view_name, build_view):
        """Let a later ticket add its own App View to the flow."""
        self.view_builders[view_name] = build_view

    def show_view(self, view_name, **view_arguments):
        """
        Switch to a registered App View. Returns False if it has no builder yet.

        Any extra arguments are handed to the builder, which is how a choice the
        user just made, such as the Bot Mode to play, reaches the new App View.
        """
        build_view = self.view_builders.get(view_name)

        if build_view is None:
            return False

        self.current_view_name = view_name
        self.window.show_view(build_view(**view_arguments))

        return True

    def close(self):
        """Stop the app. Closing an already closed app does nothing."""
        if not self.is_running:
            return

        self.is_running = False
        self.window.close()
