# Gocar
Car intersection simulation


## Setup (Debian 10)
```bash
# Install python3 libraries
pip3 install -r requirements.txt
```

## Running
```bash
./run.sh < examples/example.in

# or simply
python3 src/main.py < examples/example.in
```

## Visualisation colors
### Colors:
* `Righteous` - Green
* `Hoarder` - Yellow
* `Nervous` - Red
* `Frustrated` - Orange
* `Altruistic` - Blue

### Controls
* `SPACE` - pause visualisation
* `Right/left arrow` - move one step forward/backward
* `Up/Down arrow` - increase/decrease speed

Each car has its priority written on it.

## Design
### Small steps
Each big simulation step is divided into 4 small steps.  
Without this cars could teleport through each other without collisions.
Decisions occur on every big step

### Priority trading
Each car has some assigned priority. The lower the number the faster the car will get through the intersection.  
On each big step car agents have the opportunity to swap their priority with some other agent and pay for it in points.
The price to swap `p1` for `p2` is `|p1 - p2|/2`.  
`Altruist` offers `50%` lower price to give others more chances to pass first.
Each car tries to predict with which cars it would crash and then tries to achieve better priority than any of these cars.

### Choosing speeds
After trading priority each car chooses its new speed.  
First we choose car with the highest priority and try to assign speeds `-1`, `+0`, `+1`.

For each of these assignments other cars try to choose good speeds for themselves.
Each car tries to have different speeds and simulates simplified intersection to see if they will crash with this speed. The car then chooses the highes speed that does not result in a crash.

Finally for the highest priority car we choose the highest speed where there is no crash.
If there is no such speed all cars slow down.


## Profiles
### Righteous
Wants to have a better priority if `haste > 3`  
Agrees to let go cars with higher haste  

### Hoarder
Wants to have a better priority if `haste == 5`  
Otherwise always agrees to let go  

### Nervous
Always wants to have better priority  
Never agrees to let go  

### Frustrated
Wants to have a better priority if `haste > 3`  
Agrees to let go cars with higher haste  
Every 2 steps its haste increases by 1

### Altruistic
Wants to have a better priority if `haste == 5`  
Otherwise lets go  
Its prices are `50%` lower