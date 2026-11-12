% Ready for Task 27: the state after Task 26 (Solve every point with a for loop).
run("reset_t26.m");

for k = 1:n
    qk = solve(ks, pawPath(k, :), guess);
    qPath(k, :) = qk(:)';
    guess = qk(:)';
end
clear k qk
