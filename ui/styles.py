PRIMARY = "#2563EB"
SUCCESS = "#16A34A"
WARNING = "#EA580C"
BACKGROUND = "#F8FAFC"
CARD = "#FFFFFF"
TEXT = "#111827"


def load_css():

    return """
    <style>

    .main-title{
        font-size:42px;
        font-weight:bold;
        color:#2563EB;
        text-align:center;
    }

    .sub-title{
        font-size:20px;
        text-align:center;
        color:#475569;
    }

    .card{

        background:white;

        padding:20px;

        border-radius:12px;

        border:1px solid #E5E7EB;

        box-shadow:0px 3px 10px rgba(0,0,0,.08);

        margin-bottom:20px;

    }

    .feature{

        background:#EFF6FF;

        padding:12px;

        border-radius:8px;

        margin-top:10px;

    }

    </style>
    """