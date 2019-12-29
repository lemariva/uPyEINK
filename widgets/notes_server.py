#from flask import abort, jsonify, render_template, request
import gc
import models_btree
from microWebSrv import MicroWebSrv
from models_btree import Note

models_btree.db.connect()
models_btree.Note.create_table(True)

def _httpHandlerGetNotes(httpClient, httpResponse):
    keys_notes = Note.get_keys()
    note_html = ""
    for note_id in keys_notes:
        note = Note.get_id(note_id)[0]
        if not note.archived:
            note_html += """\
                <li class="note col-xs-12 col-sm-6 col-lg-4">
                <div class="panel panel-primary">
                <div class="panel-heading">{1}
                <a class="btn btn-danger btn-xs pull-right" href="del/{0}">&times;</a>
                </div>
                <div class="panel-body">{2}</div>
                </div>
                </li>
                """.format(note.id, note.timestamp, note.content)
    content = """\
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Notes</title>
            <link href="//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
            <div class="container content">
            <div class="page-header">
            <h1>Notes</h1>
            </div>
            <form action="add" class="form" method="post">
            <button class="btn btn-primary btn-xs" type="submit">
            <span class="glyphicon glyphicon-plus"></span> Add Note
            </button>
            <textarea class="form-control" id="content" name="content"></textarea>
            </form>
            <br />
            <ul class="list-unstyled notes">
            {0}
            </ul>
            <div style="clear:both;"></div>
            </div>
            </body>
            </html>
            """.format(note_html)
    gc.collect()
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)
    content = None
    gc.collect()
    
def _httpHandlerSaveNote(httpClient, httpResponse):
    formData = httpClient.ReadRequestPostedFormData()
    note = formData["content"]
    Note.create(content=note)
    content = """\
        <!DOCTYPE html>
        <html><head><script>window.location.href = "/";</script></head><html>
        """
    gc.collect()
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)
    content = None
    gc.collect()

def _httpHandlerDeleteNote(httpClient, httpResponse, routeArgs):
    note_id = str(routeArgs['nodeid'])
    Note.update({"id": note_id}, archived=1)
    Note.del_key(note_id)
    content = """\
        <!DOCTYPE html>
        <html>
            <head>
            <script>
                window.location.href = "/";
            </script>
            </head>
        </html>
        """
    gc.collect()
    httpResponse.WriteResponseOk(headers=None,
                                 contentType="text/html",
                                 contentCharset="UTF-8",
                                 content=content)
    content = None
    gc.collect()

routeHandlers = [
    ("/", "GET", _httpHandlerGetNotes),
    ("/add", "POST", _httpHandlerSaveNote),
    ("/del/<nodeid>", "GET", _httpHandlerDeleteNote)
]

def run():
    mws = MicroWebSrv(routeHandlers=routeHandlers, webPath="www/")
    mws.Start(threaded=True)
    gc.collect()
