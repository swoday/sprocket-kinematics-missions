% Ready for Task 28: the state after Task 27 (Solve every point with a for loop).
run("reset_t27.m");

for k = 1:n
    qk = solve(ks, pawPath(k, :), guess);
    qPath(k, :) = qk(:)';
    guess = qk(:)';
end
clear k qk
