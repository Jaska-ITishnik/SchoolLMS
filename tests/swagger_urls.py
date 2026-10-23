from root.urls import build_urlpatterns


urlpatterns = build_urlpatterns(
    debug=True,
    enable_demo_api=False,
    enable_api_docs=True,
)
