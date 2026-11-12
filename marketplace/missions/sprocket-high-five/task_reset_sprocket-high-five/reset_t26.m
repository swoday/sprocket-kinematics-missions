% Ready for Task 26: the state after Task 25 (Blend the two paw positions into pawPath).
run("reset_t25.m");

pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';
