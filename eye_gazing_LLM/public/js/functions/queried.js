let has_queried = 0;

export function get(){
    return has_queried;
}

export function increment(){
    ++has_queried;
    return has_queried;
}

export function reset(){
    has_queried = 0;
    return 0;
}

export function set(num){
    has_queried = num;
}