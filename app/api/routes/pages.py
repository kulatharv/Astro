"""Frontend HTML template rendering routes with multi-language (i18n) support."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.core.templating import render_template
from app.services.translation_service import SUPPORTED_LANGUAGES, load_translations

router = APIRouter(tags=["Pages"])


def _render_page(request: Request, template_name: str, lang: str | None = None, context: dict | None = None) -> HTMLResponse:
    templates = request.app.state.templates
    selected_lang = lang or getattr(request.state, "lang", request.cookies.get("lang", "en"))
    if lang and lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=404, detail=f"Language code '{lang}' not supported")

    if selected_lang not in SUPPORTED_LANGUAGES:
        selected_lang = "en"

    base_ctx = {
        "request": request,
        "lang": selected_lang,
        "t": load_translations(selected_lang),
        "supported_languages": SUPPORTED_LANGUAGES,
    }
    if context:
        base_ctx.update(context)

    response = render_template(templates, request, template_name, base_ctx)
    response.set_cookie(key="lang", value=selected_lang, max_age=31536000)
    return response


@router.get("/", response_class=HTMLResponse)
@router.get("/{lang}/", response_class=HTMLResponse)
def home_page(request: Request, lang: str | None = None):
    return _render_page(request, "index.html", lang=lang)


@router.get("/prediction", response_class=HTMLResponse)
@router.get("/{lang}/prediction", response_class=HTMLResponse)
def prediction_page(request: Request, lang: str | None = None):
    return _render_page(request, "prediction.html", lang=lang)


@router.get("/chat")
@router.get("/{lang}/chat")
def chat_page(request: Request, lang: str | None = None):
    target = f"/{lang}/prediction" if lang else "/prediction"
    return RedirectResponse(target, status_code=303)


@router.get("/panchang.html", response_class=HTMLResponse)
@router.get("/panchang", response_class=HTMLResponse)
@router.get("/{lang}/panchang", response_class=HTMLResponse)
def panchang_page(request: Request, lang: str | None = None):
    return _render_page(request, "panchang.html", lang=lang)


@router.get("/blogs", response_class=HTMLResponse)
@router.get("/{lang}/blogs", response_class=HTMLResponse)
def blogs_page(request: Request, lang: str | None = None):
    return _render_page(request, "blogs.html", lang=lang)


@router.get("/about", response_class=HTMLResponse)
@router.get("/{lang}/about", response_class=HTMLResponse)
def about_page(request: Request, lang: str | None = None):
    return _render_page(request, "about.html", lang=lang)


@router.get("/horoscope", response_class=HTMLResponse)
@router.get("/{lang}/horoscope", response_class=HTMLResponse)
def horoscope_page(request: Request, lang: str | None = None):
    return _render_page(request, "daily-horoscope.html", lang=lang)


@router.get("/kundali", response_class=HTMLResponse)
@router.get("/{lang}/kundali", response_class=HTMLResponse)
def kundali_page(request: Request, lang: str | None = None):
    return _render_page(request, "kundali.html", lang=lang)


@router.get("/blog/{blog_id}", response_class=HTMLResponse)
@router.get("/blogs/{blog_id}", response_class=HTMLResponse)
@router.get("/{lang}/blog/{blog_id}", response_class=HTMLResponse)
@router.get("/{lang}/blogs/{blog_id}", response_class=HTMLResponse)
def blog_detail_page(request: Request, blog_id: int, lang: str | None = None):
    return _render_page(request, "blog-detail.html", lang=lang, context={"blog_id": blog_id})
