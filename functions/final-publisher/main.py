import base64
import telegram

from google.cloud import firestore
from google.cloud import secretmanager
from telegram import utils

project_id = "tldr-278619"
secret_id = "tldrmebot_key"

client = secretmanager.SecretManagerServiceClient()
secret_name = client.secret_version_path(project_id, secret_id, "1")
secret_response = client.access_secret_version(secret_name)
payload = secret_response.payload.data.decode('UTF-8')
bot = telegram.Bot(payload)

urls_collection = firestore.Client().collection(u"urls")

# chat_id = "@tldrtest"
chat_id = "@techtldr"


def publish(doc_id):
    doc_ref = urls_collection.document(doc_id)
    doc = doc_ref.get()
    if not doc.exists:
        return
    top_image = doc.get("top_image")
    title = doc.get("title")
    url = doc.get("url")
    text = ""
    for paragraph in doc.get("summary").split("\n"):
        text = "{}\n* {}".format(text, paragraph)

    text = utils.helpers.escape_markdown(text, version=2)
    bot.send_message(chat_id=chat_id,
                     text='<b><a href="{url}">{title}</a></b>.'.format(url=url, title=title),
                     parse_mode=telegram.ParseMode.HTML,
                     disable_web_page_preview=True)
    if top_image:
        bot.send_photo(chat_id=chat_id, photo=top_image)
    bot.send_message(chat_id=chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN_V2,
                     disable_web_page_preview=True)


def function_call_publish(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    doc_id = base64.b64decode(event["data"]).decode("utf-8")
    publish(doc_id)


if "__main__" == __name__:
    publish("https___thenextweb.com_apps_2020_06_05_dropbox-is-testing-a-new-password-manager-app_")