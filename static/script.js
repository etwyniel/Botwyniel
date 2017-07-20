var pausePlayButton;
var nextButton;
var previousButton;
var mediaControl;
var progressBar;
var queue;
var nowPlaying;
var input;
var thumbnail;
var darken;
var sidebar;
var menuButton;
var playlist;

function pausePlayButtonHandler()
{
	if (!playing)
	{
		//pausePlayButton.textContent = '⏸';
		pausePlayButton.classList.remove("fa-play");
		pausePlayButton.classList.add("fa-pause");
		ws.send("MEDIA_PLAY");
	}
	else
	{
		//pausePlayButton.textContent = '▶️';
		pausePlayButton.classList.remove("fa-pause");
		pausePlayButton.classList.add("fa-play");
		ws.send("MEDIA_PAUSE");
	}
}

function nextButtonHandler()
{
	//if (queue.childNodes.length > 1)
		ws.send("MEDIA_NEXT");
}

function previousButtonHandler()
{
	ws.send("MEDIA_PREVIOUS");
}

function inputHandler(e)
{
	var keyCode = e.keyCode;
	if (keyCode == 13 && input.value != "")
	{
		var val = input.value;
		if (val.length > 64)
			val = val.substring(0, 64);
		ws.send("MEDIA_QUEUE \n" + val);
		input.value = "";
	}
}

window.addEventListener("load", function() {
	pausePlayButton = document.getElementById("pause-play-button");
	pausePlayButton.onclick = pausePlayButtonHandler;
	nextButton = document.getElementById("next-button");
	nextButton.onclick = nextButtonHandler;
	previousButton = document.getElementById("previous-button");
	previousButton.onclick = previousButtonHandler;
	input = document.getElementById("request-input");
	input.onkeydown = inputHandler;
	mediaControl = document.getElementById("media-controls");
	progressBar = document.getElementById("song-progress-bar");
	thumbnail = document.getElementById("thumbnail");
	darken = document.getElementById("darken");
	darken.onclick = darkenHandler;
	sidebar = document.getElementById("server");
	menuButton = document.getElementById("menu-icon");
	menuButton.onclick = menuButtonHandler;
	playlist = document.getElementById("playlist");
	window.setInterval(function() {
		if (playing)
		{
			progressBar.value += 1;
			if (progressBar.value == progressBar.max)
			{
				playing = false;
				//pausePlayButton.textContent = '▶️';
				pausePlayButton.classList.remove("fa-pause");
				pausePlayButton.classList.add("fa-play");
			}
		}
	}, 1000);
	queue = document.getElementById("queue");
	nowPlaying = document.getElementById("now-playing");
});

function joinChannel(id)
{
	ws.send("JOIN_CHANNEL " + server_id + " " + id);
	darken.onclick()
}

function onMessage(event)
{
	data = event.data.split(' ')
	switch (data[0])
	{
		case "JOINED_CHANNEL":
			if (mediaControl.hidden) {
				mediaControl.hidden = false;
				document.getElementById("status-info").hidden = true;
			}
			if (connectedChannel != null)
				connectedChannel.classList.remove("connected");
			connectedChannel = channelsById[data[1]];
			connectedChannel.classList.add("connected");
			//document.getElementById("status-message").innerText = "Botwyniel is connected to a voice channel on this server.";
			break;
		case "MEDIA_PLAYING":
			//pausePlayButton.textContent = '⏸';
			pausePlayButton.classList.remove("fa-play");
			pausePlayButton.classList.add("fa-pause");
			playing = true;
			break;
		case "MEDIA_PAUSED":
			//pausePlayButton.textContent = '▶️';
			pausePlayButton.classList.remove("fa-pause");
			pausePlayButton.classList.add("fa-play");
			playing = false;
			break;
		case "MEDIA_QUEUED":
			var d = event.data.split('\n');
			var duration = d[1];
			var title = d[2];
			var thumbnail_url = d[3];
			var el = document.createElement("tr");
			var n = document.createElement("td");
			var t = document.createElement("td");
			var du = document.createElement("td");
			n.appendChild(document.createTextNode((queue.childElementCount + 1).toString()));
			t.appendChild(document.createTextNode(title));
			du.appendChild(document.createTextNode((duration > 60 ? Math.floor(duration / 60).toString() + "m" : "") +
				(duration % 60 < 10 ? "0" : "") + (duration % 60).toString() + "s"));
			//el.appendChild(document.createTextNode((duration > 60 ? Math.floor(duration / 60).toString() + "m" : "") + (duration % 60).toString() + "s - " + title));
			el.appendChild(n);
			el.appendChild(t);
			el.appendChild(du);
			el.classList.add("playlist-item");
			el.setAttribute("duration", duration);
			el.setAttribute("title", title);
			el.setAttribute("thumbnail", thumbnail_url);
			queue.appendChild(el);
			queue.appendChild(document.createTextNode(""));
			playlist.style.height = (parseFloat(playlist.style.height) + 1.38) + "em";
			break;
		case "MEDIA_NEXT":
			if (queue.childNodes.length == 1)
			{
				playing = false;
				//pausePlayButton.textContent = '▶️';
				pausePlayButton.classList.remove("fa-pause");
				pausePlayButton.classList.add("fa-play");
				progressBar.value = progressBar.max;
				break;
			}
			var current = queue.removeChild(queue.childNodes[1]);
			queue.removeChild(queue.childNodes[1]);
			nowPlaying.innerText = "Now playing: " + current.getAttribute("title");
			progressBar.value = 0;
			progressBar.max = current.getAttribute("duration");
			thumbnail.src = current.getAttribute("thumbnail");
			playing = true;
			//pausePlayButton.textContent = '⏸';
			pausePlayButton.classList.remove("fa-play");
			pausePlayButton.classList.add("fa-pause");
			playlist.style.height = (parseFloat(playlist.style.height) - 1.38) + "em";
			var nodes = document.getElementsByClassName("playlist-item");
			for (var i = 0; i < nodes.length; i++)
				nodes[i].firstElementChild.innerText = i + 1;
			break;
		case "MEDIA_PREVIOUS":
			progressBar.value = 0;
			//pausePlayButton.textContent = '⏸';
			pausePlayButton.classList.remove("fa-play");
			pausePlayButton.classList.add("fa-pause");
			playing = true;
			break;
	}
}

function darkenHandler()
{
	darken.style.background = "rgba(0, 0, 0, 0)";
	sidebar.style.left = "-45%";
	setTimeout(function() { darken.style.display = "none"; sidebar.style.display = "none"; }, 300);
}

function menuButtonHandler()
{
	darken.style.display = "block";
	//darken.style.background = "rgba(0, 0, 0, 0.6)";
	sidebar.style.display = "block";
	//sidebar.style.left = "0";
	setTimeout(function () { darken.style.background = "rgba(0, 0, 0, 0.6)"; sidebar.style.left = "0"; }, 0);
}
