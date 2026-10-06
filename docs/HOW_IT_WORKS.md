# How This Works (Plain-Language Explanation)

For presenting in class or explaining to someone non-technical.

## The big picture

This project clones someone's voice from a short recording, then makes that
voice say anything you type. There are three pieces talking to each other:

```
[Your phone or laptop browser]  →  [The API running on your laptop]  →  [F5-TTS, the AI model]
        (the "front end")              (the "API": imv_api.py)          (does the actual voice work)
```

Think of it like ordering food: the front end is the menu you look at and
tap buttons on, the API is the waiter who takes your order to the kitchen and
brings back the food, and F5-TTS is the kitchen that actually cooks (generates
the audio).

## What F5-TTS actually does

F5-TTS is an AI model that does "voice cloning text-to-speech." You give it:
- a short audio clip of someone talking (5-15 seconds is enough)
- the exact words spoken in that clip (so it knows how those sounds map to
  that voice)
- new text you want spoken

...and it generates a brand new audio clip of that same-sounding voice
speaking your new text — even sentences that person never actually said.
It doesn't need hours of training data like older voice-cloning systems; it
learns the voice's characteristics from that one short sample.

## What the API (imv_api.py) does

The API is a small program that sits between the front end and F5-TTS.
F5-TTS itself doesn't know how to be a website — it's a command you run in a
terminal. So the API's whole job is:

1. **Remembers voices.** When you "add a voice," it saves your audio file and
   its transcript under a name you choose (like "mariela" or "professor").
   It keeps a simple list (`voices_log.json`) of every voice it knows about.
2. **Runs F5-TTS for you.** When you ask it to generate speech, it looks up
   the voice you picked, and runs the F5-TTS command behind the scenes with
   the right reference audio, the right transcript, and the new text you
   typed.
3. **Hands back the audio file.** Once F5-TTS finishes (this can take anywhere
   from a few seconds to a couple minutes depending on your computer), the
   API sends the resulting sound file back to whoever asked for it.

It does this over the internet using a very ordinary technique called a
"REST API" — the same kind of thing almost every app and website uses to talk
to a server. That's *why* this can work from a phone: a phone doesn't need
any special software to talk to a REST API, it just needs to be able to reach
your laptop's address on the network, the same way your phone reaches a
website.

## What the front end (index.html) does

This is the part you actually see and tap — a single web page with three
things on it:

1. A box to add a new voice (type a name, paste the exact transcript, upload
   an audio clip).
2. A box to generate speech (pick a voice from a dropdown, type any text,
   press Generate).
3. An audio player that shows up once the sound comes back, so you can play
   it right there or download it.

It's "just a web page" — no app-store install, no special phone software.
That's also why it works equally well on a laptop or a phone: it's the same
page either way, it just needs to know your laptop's network address to know
where to send requests.

## Why it wasn't working before

Two separate problems, both explained in more technical detail in
`FIX_WRITEUP.md`:

1. **The AI model's name changed.** The original code told F5-TTS "use the
   model called F5-TTS." That used to be a valid name back when this was
   written. F5-TTS's developers later renamed things (a bit like a company
   renaming a product), and "F5-TTS" stopped being a recognized name — so
   every request failed immediately, before any audio was even attempted.
2. **The default voice was broken from the start.** The very first "default"
   voice the code set up pointed at an audio file that was created completely
   empty — 0 bytes, no sound at all. So even after fixing problem #1, trying
   to use that particular voice would still fail, because there was nothing
   to clone in the first place.

Both are now fixed: the model name points at F5-TTS's current name for its
best model, and the default voice points at a real short sample that comes
bundled with F5-TTS itself.

## Why a phone can use this without installing an app

An "app" is really just a program that knows how to talk to a server over
the internet and show you a nice interface. A web page can do exactly the
same thing, as long as your phone's browser can reach the server. Since your
laptop and phone are usually on the same Wi-Fi network at home or in a
classroom, the phone's browser can talk directly to the API running on your
laptop — no app store, no installation, no extra software. Typing the page
into your phone's browser (or adding it to your home screen as a shortcut)
gets you the exact same experience a real app would give you for this
purpose.
