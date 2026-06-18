export function vidInitLLM(){
    const vid = document.getElementById('webgazerVideoContainer');

    const old_dim_obj = {
        width: parseFloat(getComputedStyle(vid).width),
        height: parseFloat(getComputedStyle(vid).height)
    };

    const dilate = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    vid.style.transformOrigin = '0 0';
    vid.style.transform = `scale(${dilate})`;

    const dim_obj = {
        width: old_dim_obj.width * dilate,
        height: old_dim_obj.height * dilate
    };

    const new_pos = {
        left: window.innerWidth - dim_obj.width,
        top: window.innerHeight - dim_obj.height
    };

    // console.log(`{
    //     dilate: ${dilate}, 
    //     old_dim_obj: {width: ${old_dim_obj.width}, height: ${old_dim_obj.height}},
    //     dim_obj: {width: ${dim_obj.width}, height: ${dim_obj.height}}, 
    //     new_pos: {left: ${new_pos.left}, top: ${new_pos.top}},
    //     window: {innerWidth: ${window.innerWidth}, innerHeight: ${window.innerHeight}}
    // }`);

    // console.log("got here");
    vid.style.position = 'fixed';
    vid.style.top = `${new_pos.top}px`;
    vid.style.left = `${new_pos.left}px`;
    // document.getElementById('webgazerVideoContainer').style.position = 'fixed';
}