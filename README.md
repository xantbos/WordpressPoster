# WordpressPoster

A small-ish script designed to automate posting content to wordpress.

Written in Python 3.5

# Dependencies

* Googletrans - https://github.com/ssut/py-googletrans
* BeautifulSoup4 - https://www.crummy.com/software/BeautifulSoup/

# Explanation

To explain what this does as-is, this will:

* Checks a series page over on https://ncode.syosetu.com/
* Parses the series' page (will touch on this later) to figure out what the last chapter uploaded was
* Rips the 'next' chapter of the series
* Uses google translate to parse the chapter contents into english
* Creates a page (for easy site navigation) with the chapter title, content, and prev/index/next directors on the top and bottom of the page
* Creates a post announcing the page with a direct link to it
* Edits the series page with the new chapter, name, and link
* Uploads the chapter to Wordpress

Due to the way the scraper identifies chapter content on your blog (aka it only likes its own format) you either update the parse_series_page() function in WordPressAPI or update your chapter list on your series page to conform with the format: `Chapter X - Title`

Going further on the pre-requisites for this to run as-is on your blog you require:

* A wordpress account with a blog
* A wordpress developer app
* A series parent page (https://blog.wordpress.com/series/)
* A series page (https://blog.wordpress.com/series/seriesname)

The series page can be blank, can have a summary, whatever. The only requirement is that the last direct \<a\> link on the series page (at least if you intend to just use this as supplied) is a chapter with the above commented formatting.

This does *not* require a paid wordpress blog, but due to that your wordpress username and password are stored in the config in plaintext. If you require better authentication for client-side applications, this ain't it chief.

You 'should' understand Wordpress' OAuth2 https://developer.wordpress.com/docs/oauth2/ (or not because this script simplifies it)

Once that's all well and good, set up an account (if you lack one) here: https://wordpress.com/start
And follow along here to set up an app: https://developer.wordpress.com/apps/
###### If you don't know what to make your redirect URL just set it to the home of your blog

First things first, discussing the config.js

```
{
    "wordpressAPI":{
        "username": "",
        "password": "",
        "clientId": 0,
        "clientSecret": "",
        "redirectUri": ""
    },
	"wordpressConfig":{
		"bloghome": ""
	},
	"seriesData":{
		"seriesname": "",
		"seriesslug": "",
		"seriesraw" : "https://ncode.syosetu.com/",
		"chapterstart" : "",
		"srclang": ""
	}
}

```

"wordpressAPI" is straightforward enough as a name, I hope. If you followed the above bits and made your app, this is easy to fill in.

> "username" : ""

Make this your wordpress login username

> "password" : ""

Make this your wordpress login password

> "clientId" : 0

> "clientSecret" : ""

> "redirectUri" : ""


Change these values to the matching app values. Note clientId must be an int, not a string, hence no "". And Uri = Url.

---

"wordpressConfig" is kind of repetitive but I didn't have the brainpower to think of something better. 

> "bloghome" : ""

This should be the root url of your blog (like "https://blogname.home.blog" or whatever your domain is)


---

Now the last part, "seriesData".

This one is a little more complicated compared to the other two, but not by much.

> "seriesname": ""

Put the full series name here (or at least, whatever you want the chapter titles to be)

> "seriesslug": ""

The html slug of your series (Example: https://blog.wordpress.com/series/seriesname would mean "seriesname" is the slug)

> "seriesraw" : "https://ncode.syosetu.com/"

This is the direct link to the series' raw page. The scraper will handle the rest.

> "chapterstart" : ""

If you wanted to start midway in a series, this is where you'd set it. Set to 1 if you intend to start from the beginning.
###### Please note this script assumes the first chapter on syosetu is 'Chapter 1'. If it's called 'Chapter 0' it's still considered 'Chapter 1'.

> "srclang": ""

This should always be "ja" unless you're changing the source site and changing the Ripper class, as this only works with syosetu and that is only in Japanese.

---

# Limitations

This piggybacks on an unrelated API, so sending too much content will get you blocked. I've set the timer to half a day delay which seems to work consistently through the day for a syosetu chapter.
If you send several chapters in rapid succession you will find yourself restricted from access for anywhere from 24-48 hours if not more.

Wordpress may restrict your app's access if you abuse the endpoints, and this Basic Auth setup is _only_ meant for server-side 'development' applications.

This script isn't very flexible in handling other configurations and is designed around a more or less specific setup.

---

# Extra Functionality

If you're someone who wants to do the translating beforehand and just let the bot go to town, there's a function called parse_existing_file() in Ripper. This allows you to use a folder that shares the series' slug name to use provided txt files instead of ripping from the internet and relying on MTL.

So in the same folder as main.py you'd have a folder that uses the slug in your config. Within that folder, use numbered chapters from X-Y, X being the first chapter you want to post (whether it be 1 or 600), and just keep incrementing as you go. So like `1.txt`

The script will take the _very first line_ as the chapter title **as is** while the rest of the text file will be taken as is, spacing and all.

I recommend this if you just want to set up a simple automation loop for uploading content and have translations sitting around.
