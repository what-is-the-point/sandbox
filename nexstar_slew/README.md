# Nexstar Slew Track

Tracking based on slew commands only.  

The GOTO command uses a 'GoTo Approach' algorithm that helps with backlash and always approaches a target coordinate from the same angle.
When streaming a sequence of Az/El goto commands, this causes the mount to swing a few degrees away from the target coordinate so that it can slowly 'settle' back onto the target.
Even if the delta from the current angle to the target angle is only a fraction of a degree, it will still slew ~5 degrees off the new coordinate and then slowly settle.
Net result when rapidly update target Az/El is a supper wobbly track that never actually settles on the desired coordinate.

This project will attempt to reimplement 'goto' commands using ONLY slew commands (for now fixed rate, may switch to variable rate if it makes sense).
This way it should avoid the GOTO approach bits and only slew.

Basic approach (pun intended) is to read the current az/el, compute the direction (up, down,, left, right) and distance (in degrees) to the target coordinate then issue the appropriate slew commands to track the target.  The rate of the slew commands will be based on the distance to the target in degrees.  If its way off it will slew with max speed.  as it gets close to the target coordinate, it will slowly decrease the slew speed to gently settle on the target.  This will likely need some serious fine tuning.
