// import { relatively } from "./relative";

// export const absoluteMouse = {
//     x: 0, 
//     y: 0,
//     mouseDataBuffer: [],
//     mousePush: function (clock) {
//         this.mouseDataBuffer.push({
//             x: this.x, 
//             y: this.y, 
//             time: clock
//         });
//     },
//     clearMouseData: function() {
//         this.mouseDataBuffer = [];
//     }
// }

// export const relativeMouse = {
//     x: -1, 
//     y: -1,
//     mouseDataBuffer: [],
//     mousePush: function (clock) {
//         this.mouseDataBuffer.push({
//             x: this.x, 
//             y: this.y, 
//             time: clock
//         });
//     },
//     clearMouseData: function () {
//         this.mouseDataBuffer = [];
//     }
// }

// const container = document.getElementById('llm-response');
// const rect = container.getBoundingClientRect();

// document.clien

// document.addEventListener('mousemove', (e) =>{
//     e.preventDefault();

//     const x = e.clientX;
//     const y = e.clientY;

//     absoluteMouse.x = x;
//     absoluteMouse.y = y;
    
//     const relObj = relatively(x,y);

//     relativeMouse.x = relativeX;
//     relativeMouse.y = relativeY;

//     // console.log(`Rect: {left: ${rect.left}, top: ${rect.top}, right: ${rect.right}, bottom: ${rect.bottom}}, Relative: {x: ${relative_x}, y: ${relative_y}}`);
// });



// // var time = 600;export function relativeMousePush(clock){

// // const destroy_this = setInterval(()=>{
// //         if(time-- <=0) (clearInterval(destroy_this));
// //         console.log(`Absolute: {X:${x} / ${window.innerWidth}, ${y} / ${window.innerHeight}}, Relative: {X: ${relative_x}, Y: ${relative_y}}`);
// // }, 100); 

let x = -1;
let y = -1;

document.addEventListener('mousemove', (e)=>{
    e.preventDefault();
    x = e.clientX;
    y = e.clientY;
})

export function getMouse(){
    return {x: x, y: y};
}