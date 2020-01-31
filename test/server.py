import os
import logging
from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request

app = Sanic()
logger.setLevel(logging.CRITICAL)


@app.route("/basic")
async def basic(request: Request) -> None:
    return response.text("Hello, World!")


@app.route("/headers-test")
async def headers_test(request: Request) -> None:
    return response.text(
        "HeadersTest", headers={"x-test-1": "foo", "OTHER-TEST": "bar"}
    )


@app.route("/basic-json")
async def basic_json(request: Request) -> None:
    return response.json({"hello": "world", "foo": True}, sort_keys=True)


@app.route("/error-400")
async def error_400(request: Request) -> None:
    return response.text("", 400)


@app.route("/error-401")
async def error_401(request: Request) -> None:
    return response.text("", 401)


@app.route("/response-latin-1")
async def response_latin_1(request: Request) -> None:
    return response.raw(
        "ñáéíóúß".encode("latin1"), content_type="text/plain; charset=latin1"
    )


@app.route("/request-latin-1", methods=["POST"])
async def request_latin_1(request: Request) -> None:
    if request.headers["Content-Type"] != "text/plain; charset=latin1":
        return response.text("FAIL")

    if request.body.decode("latin1") != "áéíóúñü":
        return response.text("FAIL")

    return response.text("OK")


@app.route("/request-utf-8-default", methods=["POST"])
async def request_utf_8_default(request: Request) -> None:
    if request.headers["Content-Type"] != "text/plain; charset=utf-8":
        return response.text("FAIL")

    if request.body.decode("utf-8") != "áéíóúñü":
        return response.text("FAIL")

    return response.text("OK")


@app.route("/request-utf-8-default-2", methods=["POST"])
async def request_utf_8_default_2(request: Request) -> None:
    if request.body.decode("utf-8") != "áéíóúñü":
        return response.text("FAIL")

    return response.text("OK")


@app.route("/response-utf-8-default")
async def response_utf_8_default(request: Request) -> None:
    # Do not specify charset=
    return response.raw("ñáéíóúß".encode("utf-8"), content_type="text/plain")


@app.route("/response-big5")
async def response_big_5(request: Request) -> None:
    return response.raw("常用字".encode("big5"), content_type="text/plain; charset=big5")


@app.route("/")
async def root(request: Request) -> None:
    if request.args.get("foo") == "bar":
        return response.text("OK")

    return response.text("FAIL")


@app.route("/redirect-301")
async def redirect_301(request: Request) -> None:
    return response.redirect("/basic", status=301)


@app.route("/redirect-302")
async def redirect_302(request: Request) -> None:
    return response.redirect("/basic", status=302)


@app.route("/redirect-308-2", methods=["POST"])
async def redirect_308_2(request: Request) -> None:
    return response.text("Redirect successful")


@app.route("/redirect-308", methods=["POST"])
async def redirect_308(request: Request) -> None:
    return response.redirect("/redirect-308-2", status=308)


@app.route("/no-user-agent")
async def no_user_agent(request: Request) -> None:
    if "User-Agent" in request.headers:
        return response.text("FAIL")

    return response.text("OK")


@app.route("/content-length", methods=["POST"])
async def content_length(request: Request) -> None:
    if "Content-Length" not in request.headers:
        return response.text("FAIL")

    if len(request.body) != int(request.headers["Content-Length"]):
        return response.text("FAIL")

    return response.text("OK")


@app.route("/echo", methods=["POST"])
async def echo(request: Request) -> None:
    return response.text(request.body.decode("utf-8"))


@app.route("/zero-bytes-json")
async def zero_bytes_json(request: Request) -> None:
    return response.text("", headers={"Content-Type": "application/json"})


@app.route("/sorted-headers")
async def sorted_headers(request: Request) -> None:
    headers = sorted(k.lower() + ": " + v for k, v in request.headers.items())
    return response.text("\n".join(headers), headers={"Content-Type": "text/plain"})


app.static("/image.png", "test/image.png")


def main() -> None:
    if "SKIP_PIDFILE" not in os.environ:
        pidfile = os.path.join(os.path.dirname(__file__), "server.pid")
        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), access_log=False)


if __name__ == "__main__":
    main()
