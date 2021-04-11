// name & version variables must be set in sketch

function keyPressed(){
    if(key == 's'){
        save(`${name}-${version}.png`);
    }
}
