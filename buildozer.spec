[app]
title = OneTap OPL
package.name = onetapopl
package.domain = org.onetap

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = requirements = python3==3.11.4,kivy==2.3.0,plyer,pillow,reportlab

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/icon.jpeg

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
