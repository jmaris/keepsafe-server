# keepsafe-server

## Description

A REST powered fully encrypted password manager : Server

## Requirements

  * pymysql (`pip install pymysql`)
  * captcha (`pip install captcha`)
  * passlib (`pip install passlib`)
  * falcon (`pip install falcon`)
  * gunicorn (`pip install gunicorn`)
  * sqlalchemy (`pip install sqlalchemy`)

## Run the API server

`gunicorn model:app`