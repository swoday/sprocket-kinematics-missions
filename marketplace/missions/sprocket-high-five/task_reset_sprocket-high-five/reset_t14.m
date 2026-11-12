% Ready for Task 14: the state after Task 13 (Solve every point with a for loop).
run("reset_t13.m");

for k = 1:n
    qk = solve(ks, pawPath(k, :), guess);
    qPath(k, :) = qk(:)';
    guess = qk(:)';
end
clear k qk
