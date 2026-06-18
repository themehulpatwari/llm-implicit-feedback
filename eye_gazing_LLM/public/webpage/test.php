<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>Eye-Gazing Task</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="/public/css/general.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">
    </head>
    <style>
        /* * {
            box-sizing: border-box;
        } */


        .scroll {
            overflow: hidden;
            overflow-y: scroll;
            height: 600px; 
            width: 1000px; 
            margin: 20px;
            font-size: 24px; 
            font-family: Arial;
            padding: 0px;
            line-height: 1.5;
            overflow-anchor: none;
            /* -ms-transform: translate3d(0, 0, 0);
            transform: translate3d(0, 0, 0);
            -webkit-transform: translate3d(0, 0, 0);
            -o-transform: translate3d(0, 0, 0); */
            /* padding-right: 20px; */
            /* resize: none; */
            scrollbar-gutter: stable both-edges;
            scrollbar-width: thin;
        }
    </style>
    
    <script src='/public/js/events/scrollbar.js' defer> </script>
    
    <body>
        <div id='scroll' class="scroll">
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc vitae laoreet mi. Ut ac arcu rutrum, vehicula risus et, congue massa. Nulla eget purus at mauris aliquet rhoncus. Nulla vitae sapien vel eros dapibus semper. Etiam ornare facilisis metus mollis finibus. Nam massa urna, accumsan aliquam orci vitae, vestibulum bibendum neque. Curabitur consequat ex sed metus fermentum gravida.

Sed nunc nibh, laoreet sed ante at, volutpat volutpat risus. Vivamus urna ligula, scelerisque ac tempus eget, porta ac eros. Nam iaculis vulputate orci, a tempor ligula condimentum vel. Donec neque dolor, gravida ultricies velit at, malesuada volutpat augue. Sed cursus consectetur mi id tristique. Etiam sed justo elit. Sed rutrum, justo a lobortis lobortis, tortor sapien sodales magna, imperdiet iaculis dui est quis ante. Integer libero dui, vestibulum sit amet neque a, accumsan interdum libero. Proin nisi ex, ullamcorper consequat lectus sit amet, pretium volutpat ante. Maecenas laoreet, sem sit amet dictum blandit, mi dolor viverra massa, placerat varius lorem urna laoreet ipsum.

Fusce sodales magna id sapien lacinia, in bibendum est varius. Ut ac odio vel turpis condimentum iaculis. Cras in elit eget lectus tristique tincidunt tincidunt a leo. Duis tempus condimentum nibh, vulputate facilisis augue pharetra nec. Mauris laoreet vitae massa a convallis. In at tellus mi. Donec nibh felis, luctus a finibus vitae, semper porttitor dolor. Nullam gravida nisi a massa laoreet, a feugiat ante finibus. Ut sagittis est libero, semper vestibulum nulla porta id. Curabitur faucibus nec eros eu finibus. Pellentesque tristique in augue eget condimentum. Aenean sagittis felis et lobortis dictum. Proin ornare suscipit leo ut fermentum. Nunc sapien turpis, tincidunt id odio eu, fermentum maximus diam.

Proin quis egestas tortor, id fringilla metus. Nam porttitor sem dui, sed imperdiet est laoreet eu. Nullam tempus vehicula mi. Donec tempus lobortis odio, et dignissim velit pellentesque at. Quisque in erat sollicitudin, placerat ante at, efficitur justo. Vivamus libero dolor, condimentum nec sollicitudin sit amet, pretium a odio. Maecenas ullamcorper libero dolor, at convallis urna consequat vel. Maecenas nec arcu venenatis, varius augue at, pharetra odio. Duis vitae ex felis. Nullam maximus dapibus convallis. Sed eu eros non enim dapibus tempus in eget nulla. Suspendisse id nisl ac ipsum auctor dignissim eget ut mauris.

Integer at ex quis dui vestibulum ultrices ut a nulla. Pellentesque nibh nunc, malesuada eget elit sit amet, finibus facilisis ex. Morbi viverra diam eu magna pretium, vitae egestas ipsum aliquet. Ut et nibh blandit, elementum erat eget, faucibus nulla. Mauris vitae commodo enim. Nullam et quam lorem. Nulla vel massa vehicula, ultrices leo sit amet, aliquet libero. Sed vitae faucibus metus. Suspendisse potenti. Donec maximus aliquet libero nec facilisis.
    </div>

    <textarea id='test'></textarea>

    <p style="font-size: 22px; font-family: Consolas, monospace;">
        Width of the text is:
        <span class="output"></span>
    </p>

    <button onclick="getTextWidth()">
        Calculate text width using span
    </button>

    <button onclick="getCharacterWidth(document.getElementById('test').value)">
        Calculate text width using Canvas
    </button>

    </body>

    <script>
        function getTextWidth() {
            const string = document.getElementById('test').value;
            const text = document.createElement("span");
            document.body.appendChild(text);

            text.style.fontFamily = '"Consolas", monospace';
            text.style.fontSize = 30 + "px";
            text.style.height = 'auto';
            text.style.width = 'auto';
            text.style.position = 'absolute';
            text.style.whiteSpace = 'no-wrap';
            text.innerHTML = string;

            // const width = Math.ceil(text.clientWidth);
            const width = text.clientWidth;
            const formattedWidth = width + "px";

            document.querySelector('.output').textContent = formattedWidth;

            // const data = {fontFamily: text.style.fontFamily, fontSize: text.style.fontSize, string: string, width: width};
            // console.log(JSON.stringify(data, null, 2));

            document.body.removeChild(text);
        } 

        //SUBPIXEL ACCURATE. USE THIS ONE
        function getCharacterWidth(char, fontSize = 22, fontFamily = "Consolas, monospace") {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext("2d");
            context.font = `${fontSize}px ${fontFamily}`;

            const width = context.measureText(char).width;
            const formattedWidth = width + "px";
            document.querySelector('.output').textContent = formattedWidth;
            // return ;
        }

        const paragraph = document.getElementById("scroll");
        // const output = document.getElementById("output");
        
const char_interval = 10;

paragraph.addEventListener("click", (event) => {
    const caret = document.caretPositionFromPoint(event.clientX, event.clientY);
    if (!caret || !caret.offsetNode || !caret.offsetNode.textContent) {
        console.log("Nothing detected");
        return;
    }

    const index = caret.offset;
    const string = caret.offsetNode.textContent;

    const range = document.createRange();
    range.setStart(caret.offsetNode, index);

    const baseline_top = range.getBoundingClientRect().top;
    const baseline_bottom = range.getBoundingClientRect().bottom;

    let start = index;
    let end = index;
    let interval_remaining = char_interval;

    // Expand backwards
    while (start > 0 && interval_remaining > 0) {
        range.setStart(caret.offsetNode, start - 1);
        if (range.getBoundingClientRect().top !== baseline_top) break;
        start--;
        interval_remaining--;
    }

    interval_remaining = char_interval;

    // Expand forwards
    while (end < string.length && interval_remaining > 0) {
        range.setEnd(caret.offsetNode, end + 1);
        // console.log(`{baseline: ${baseline_bottom}, bottom: ${range.getBoundingClientRect().bottom}, end: ${end}}`);
        if (range.getBoundingClientRect().bottom !== baseline_bottom) break;
        end++;
        interval_remaining--;
    }

    console.log(string.substring(start, end));
});


    </script>
</html>
