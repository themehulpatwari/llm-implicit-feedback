const char_interval = 10;

export function detect_characters(abs_x, abs_y, rel_x, rel_y){
    if(rel_x < 0 || rel_y < 0){
        return {index: '', string: ''};
    }

    const caret = document.caretPositionFromPoint(abs_x, abs_y);
    if (!caret || !caret.offsetNode || !caret.offsetNode.textContent) {
        // console.log("Nothing detected");
        return {index: '', string: ''};
    }

    const index = caret.offset;
    let string = caret.offsetNode.textContent;
    // const caret_two = document.caretPositionFromPoint(150, 150);
    // console.log(`{index: ${caret.offset}, string: ${caret.offsetNode}}`)

    const range = document.createRange();
    range.setStart(caret.offsetNode, index);

    const baseline_top = range.getBoundingClientRect().top;
    const baseline_bottom = range.getBoundingClientRect().bottom;

    let start = index;
    let end = index;
    let interval_remaining = char_interval;

    while (start > 0 && interval_remaining > 0) {
        range.setStart(caret.offsetNode, start - 1);
        if (range.getBoundingClientRect().top !== baseline_top) break;
        start--;
        interval_remaining--;
    }

    interval_remaining = char_interval;

    while (end < string.length && interval_remaining > 0) {
        range.setEnd(caret.offsetNode, end + 1);
        // console.log(`{baseline: ${baseline_bottom}, bottom: ${range.getBoundingClientRect().bottom}, end: ${end}}`);
        if (range.getBoundingClientRect().bottom !== baseline_bottom) break;
        end++;
        interval_remaining--;
    }

    string = '"' + string.substring(start, end).trim() + '"';

    return {index: index, string: string};
}


// const determine_font = document.getElementById('response');
// const for_font_style = window.getComputedStyle(determine_font);
// const char_size = parseFloat(for_font_style.fontSize);
// const char_width = getTextWidth("p", `${char_size}px ${for_font_style.fontFamily}`);

// function getTextWidth(text, font) {
//     const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
//     const context = canvas.getContext("2d");
//     context.font = font;
//     const metrics = context.measureText(text);
//     return metrics.width;
// }

// function getTextWidth(char, fontSize = 22, fontFamily = "Consolas, monospace") {
//     const canvas = document.createElement("canvas");
//     const context = canvas.getContext("2d");
//     context.font = `${fontSize}px ${fontFamily}`;

//     const width = context.measureText(char).width;
//     return width;
//     // const formattedWidth = width + "px";
//     // document.querySelector('.output').textContent = formattedWidth;
//     // return ;
// }

// detect_character()

// export function detect_character(dom, rel_x, rel_y, response){
//     const style = window.getComputedStyle(dom);
//     // const fontSize = parseFloat(style.fontSize);
//     const lineHeight = parseFloat(style.lineHeight);
//     const padding_top = parseFloat(style.paddingTop);
//     const padding_left = parseFloat(style.paddingLeft);
//     // const font_width = getTextWidth("I", `${fontSize}px ${style.fontFamily}`);

//     let char_index_inline = 0
//     if(padding_left + char_width <= rel_x){
//         char_index_inline =  rel_x - (padding_left + char_width)   + 1
//     }

//     // const charsPerLine = Math.floor(dom.scrollWidth / font_width);
//     // const lineNumber = Math.floor((rel_y + padding_top) / lineHeight);
//     // const charIndexInLine = Math.floor((rel_x - padding_left) / font_width);
//     // const absoluteCharIndex = (lineNumber * charsPerLine) + charIndexInLine;

//     // if (absoluteCharIndex >= 0 && absoluteCharIndex < response.length) {
//     //     const data = {absoluteCharIndex: absoluteCharIndex, font_size: font_size, font_width: font_width, scrollWidth: dom.scrollWidth, lineHeight: lineHeight, 
//     //         padding_left: padding_left, padding_top: padding_top, charsPerLine: charsPerLine, lineNumber: lineNumber, charIndexInLine: charIndexInLine, rel_x: rel_x, rel_y: rel_y,
//     //     fontFamily: for_font_style.fontFamily};
//     //     console.log(JSON.stringify(data,null,2));
//     //     return response.charAt(absoluteCharIndex);
//     // } else {
//     //     return '';
//     // }

//     // const style = getComputedStyle(dom);

//     // const width = dom.scrollWidth;
//     // const padding_left = parseFloat(style.paddingLeft);
//     // const padding_right = parseFloat(style.paddingRight);
//     // const font_height = parseFloat(style.fontSize);

//     // const char_per_line = Math.floor(width /font_width)

//     // let char_index_inline = 0;
//     // if(0 <= rel_x && rel_x < font_width + padding_left){
//     //     char_index_inline = 0;
//     // } else if((width - (font_width + padding_right)) <= rel_x){
//     //     char_index_inline = char_per_line - 1;
//     // } else{
//     //     char_index_inline = Math.floor((rel_x - (font_width + padding_left)) / font_width) + 1;
//     // }

//     // const data = {char_per_line: char_per_line, char_index_inline: char_index_inline, font_width: font_width, padding_left: padding_left, padding_right: padding_right, rel_x: rel_x}

//     // const rect = dom.getBoundingClientRect();
//     // const height = dom.scrollHeight;
//     // const width = dom.scrollWidth;
    
//     // // const font_size = parseFloat(dom.style.fontSize);
//     // const line_height = parseFloat(style.lineHeight);
    
//     // const char_per_line = Math.floor(width / font_size);
    
//     // // const line_index = rel_y >= num_lines ? num_lines / line_height : Math.floor(rel_y / line_height);
//     // const num_lines = Math.floor(response.length / char_per_line);
//     // const line_index = Math.floor(rel_y / line_height); 
//     // if(line_index > num_lines) {return '';}

//     // const char_index_inline = Math.floor(rel_x / char_per_line);
//     // const char_index = char_per_line * line_index + char_index_inline;


//     // const start = Math.max(char_index - char_interval, char_per_line * line_index);
//     // const end = Math.min(char_index + char_interval, char_per_line * (line_index + 1), response.length); 

//     // const data = {
//     //     width: width, 
//     //     font_size: font_size, 
//     //     line_height: line_height, 
//     //     char_per_line: char_per_line, 
//     //     num_lines: num_lines, 
//     //     line_index: line_index,
//     //     char_index_inline: char_index_inline,
//     //     char_index: char_index,
//     //     start: start,
//     //     end: end
//     // }

//     // console.log(`{start: ${start}, end: ${end}, length: ${response.length}}`)
    

//     // console.log(`{font_size: ${font_size}, \n line_height: ${line_height}, \n char_per_line: ${char_per_line}, \n num_lines: ${num_lines}, \n line_index ${line_index}, 
//     //     \n char_index_inline: ${char_index_inline}, \n char_index: ${char_index}, \n start: ${start}, \n end: ${end}}`);

//     // console.log(style)

//     // return response.substring(start, end);


//     // const response_lines = num_lines / line_height;
//     // const dom_lines = rect.height / line_height;
//     // const num_lines = Math.min(response_num_lines, dom_lines);
//     // const height = Math.min(rect.height, num_lines);

//     // const line_height = parseFloat(dom.style.lineHeight);
//     // const num_lines = (font_size * line_height) / dom.getBoundingClientRect().height;
//     // const line_index = Math.floor(rel_y / )
// }