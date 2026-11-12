% Ready for Task 13: the state after Task 12 (Prepare the path points with linspace).
run("reset_t12.m");

n = 25; s = linspace(0, 1, n)';
pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';
qPath = zeros(n, 3); guess = [0 40 -80];
