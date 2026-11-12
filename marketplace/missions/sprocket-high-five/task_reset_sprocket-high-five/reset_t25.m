% Ready for Task 25: the state after Task 24 (Blend the two paw positions into pawPath).
run("reset_t24.m");

pawPath = (1 - s).*pawStance(:)' + s.*padPosition(:)';
