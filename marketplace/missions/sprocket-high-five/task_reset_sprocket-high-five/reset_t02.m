% Ready for Task 02: the state after Task 01 (Import Sprocket with smimport).
if ~exist("urdfFile", "var") || ~isfile(urdfFile)
    setup_sprocket_high_five
end
mdl = "Sprocket";
if ~bdIsLoaded(char(mdl))
    smimport(urdfFile, "ModelName", mdl);
end
