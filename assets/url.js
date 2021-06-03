(function (window, document) {
    function IsPC() {
        var userAgentInfo = navigator.userAgent;
        var Agents = ["Android", "iPhone",
            "SymbianOS", "Windows Phone",
            "iPad", "iPod"
        ];
        var flag = true;
        for (var v = 0; v < Agents.length; v++) {
            if (userAgentInfo.indexOf(Agents[v]) > 0) {
                flag = false;
                break;
            }
        }
        return flag;
    }

    var ispc = IsPC();
    var calHeight = function () {
        if (ispc) {
            var contentHeight = document.body.clientHeight - 150;
        } else {
            var contentHeight = document.body.clientHeight - 40;
        }
        var videoH = get('video');

        var footerH = get('footer').offsetHeight
        videoH.style.height = (document.body.clientHeight - footerH - 40) + 'px'
        var topNh = get('top_nav').offsetHeight
        var calVideoWidth = contentHeight * 9 / 16;
        var player = document.getElementById('player')
        var footer = get('footer')
        if (player) {
            player.addEventListener('canplay', function () {
                footer.style.marginTop = (260) + 'px';
            })
            player.style.maxHeight = contentHeight + 'px'
            player.style.maxWidth = calVideoWidth + 'px'

        }
    }
    if (top != self) {
        window.top.location.replace(self.location.href);
    }

    var get = function (id) {
        return document.getElementById(id);
    }
    var bind = function (element, event, callback) {
        return element.addEventListener(event, callback);
    }
    var auto = true;
    var player = get('player');

    var randomm = function () {
        player.src = 'video.php?_t=' + Math.random();
        player.play();
    }
    bind(get('next'), 'click', randomm);
    bind(player, 'error', function () {
        randomm();
    });
    bind(get('switch'), 'click', function () {
        auto = !auto;
        this.innerText = '连续: ' + (auto ? '开' : '关');
    });
    bind(player, 'ended', function () {
        if (auto) randomm();
    });
    calHeight()

    document.onkeydown = function (e) {
        console.log(e)
        if (e.keyCode == '40') {
            randomm()
        }
    }

    if (!ispc) {
        var hvtcenter = get('hvtcenter')
        if (hvtcenter) {
            hvtcenter.style.display = 'none'
        }
    }
})(window, document);

var goto = function (type) {
    var homeBtn = document.getElementById("home")
    var aboutusBtn = document.getElementById("about_us")
    var messageBtn = document.getElementById("message_btn")
    var video = document.getElementById('video')
    var usDiv = document.getElementById('us')
    var messageDiv = document.getElementById('message')
    switch (type) {
        case 'home':
            video.style.display = 'block';
            usDiv.style.display = 'none';
            messageDiv.style.display = 'none';
            homeBtn.className = 'nav-item active';
            aboutusBtn.className = 'nav-item cancel';
            messageBtn.className = 'nav-item cancel';
            break;
        case 'aboutus':
            video.style.display = 'none';
            usDiv.style.display = 'block';
            messageDiv.style.display = 'none';
            aboutusBtn.className = 'nav-item active';
            homeBtn.className = 'nav-item cancel';
            messageBtn.className = 'nav-item cancel';
            break;
        case 'message':
            video.style.display = 'none';
            usDiv.style.display = 'none';
            messageDiv.style.display = 'block';
            messageBtn.className = 'nav-item active';
            aboutusBtn.className = 'nav-item cancel';
            homeBtn.className = 'nav-item cancel';
            break;
    }

}
