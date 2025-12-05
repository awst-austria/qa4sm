import io
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def speed_up_matplotlib():
    """
    Speed up tests:

    - Keep Matplotlib functional.
    - Generate one tiny PNG in memory.
    - For all subsequent Figure.savefig / plt.savefig calls, write this PNG
      instead of actually rendering the figure.
    """
    import matplotlib
    matplotlib.use("Agg")  # does not require display (no GUI/window)

    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure

    # original methods
    original_plt_savefig = plt.savefig
    original_fig_savefig = Figure.savefig

    # 1) Create a tiny valid PNG buffer once
    buf = io.BytesIO()
    fig, ax = plt.subplots()
    fig.savefig(buf, format="png")
    plt.close(fig)
    png_bytes = buf.getvalue()

    def fast_savefig(self_or_fname, fname=None, *args, **kwargs):
        """
        Works both as Figure.savefig(self, fname, ...) and plt.savefig(fname, ...).
        """
        # Figure.savefig(self, fname, ...)
        if fname is not None:
            target = fname
        else:
            # plt.savefig(fname, ...)
            target = self_or_fname

        # If a file-like object is passed, just write into it
        if hasattr(target, "write"):
            target.write(png_bytes)
            return

        # Otherwise assume it's a path-like
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(png_bytes)

    # Patch both entry points
    plt.savefig = fast_savefig  # type: ignore[assignment]
    Figure.savefig = fast_savefig  # type: ignore[assignment]

    try:
        yield
    finally:
        # Restore original behaviour
        plt.savefig = original_plt_savefig  # type: ignore[assignment]
        Figure.savefig = original_fig_savefig  # type: ignore[assignmen