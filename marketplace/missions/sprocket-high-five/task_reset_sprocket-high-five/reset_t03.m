% Ready for Task 03: the state after Task 02 (Import Sprocket with smimport).
run("reset_t02.m");

if ~exist("urdfFile", "var") || ~isfile(urdfFile)
    setup_sprocket_high_five
end
mdl = "Sprocket";
if ~bdIsLoaded(char(mdl))
    smimport(urdfFile, "ModelName", mdl);
end
