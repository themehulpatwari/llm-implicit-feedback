const bar = document.getElementById('scroll');

// console.log(bar);

bar.addEventListener('scroll', (e)=>{
    e.preventDefault();

    // console.log('yo')

    const percentage = bar.scrollTop / bar.scrollHeight;
    const sumtin = bar.clientHeight / bar.scrollHeight;
    const new_scrollHeight = bar.scrollHeight - bar.clientHeight;
    const new_percentage = bar.scrollTop / new_scrollHeight * 100;
    const diff = new_scrollHeight - bar.scrollTop;

    console.log(`
        {bar.scrollTop: ${bar.scrollTop}, 
        bar.scrollHeight: ${bar.scrollHeight}, 
        percentage: ${percentage}, 
        bar.clientHeight: ${bar.clientHeight},
        sumtin: ${sumtin},
        new_scrollHeight: ${new_scrollHeight},
        new_percentage: ${new_percentage},
        diff: ${diff}
        }`);
})

if (navigator.userAgent.indexOf('Firefox') !== -1) {
    document.getElementById('scroll').style.paddingRight = '20px';
}


