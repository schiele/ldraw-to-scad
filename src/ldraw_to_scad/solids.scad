use <lib.scad>
solid__stud =
    [openscad(translate([0,0,-eps()], o=cylinder(4+eps(), r=6)),2)];
solid__stud2 =
    [openscad(translate([0,0,-eps()], o=linear_extrude(4+eps(),
        o=difference(o=[for(i=[6,4]) circle(r=i)]))),2)];
solid__stud3 =
    [openscad(translate([0,0,-eps()], o=cylinder(4+eps(), r=4)),2)];
solid__stud4 =
    [openscad(translate([0,0,-eps()], o=linear_extrude(4+eps(),
        o=difference(o=[for(i=[8,6]) circle(r=i)]))),2)];
solid__3641 = [for(i=[0:31])
    ldraw_rot([[18-4*(i%2), 0], [18-4*(i%2), -8],
               [10, -8], [10, -4], [8, -3], [8, 3], [10, 4], [10, 8],
               [14+4*(i%2),8],[14+4*(i%2),0]],
              [i*45/4 - eps(), i*45/4 + 45/4 + eps()])];
solid__3788 = [
    for(i=[-30,30])
        [1,16,i,0,0,0,0,1,0,1,0,-1,0,0, ldraw_lib__stug_1x2(realsolid)],
    [1,16,0,8,0,0,0,1,0,1,0,-1,0,0, ldraw_lib__stug_2x2(realsolid)],
    [1,16,0,12,0,1,0,0,0,-1,0,0,0,1, ldraw_lib__stud4(realsolid)],
    for(i=[-16, 20]) ldraw_lin(
        [[-20, 8], [-20, 0], [-40, 0], [-40, 16],
         [40, 16], [40, 0], [20, 0], [20, 8]],
        [i-4, i]),
    ldraw_lin(
        [[-20, 8], [-20, 0], [-40, 0], [-40, 4],
         [-24, 4], [-24, 6], [-20, 16], [-16, 16], [-16, 12],
         [16, 12], [16, 16], [20, 16], [24, 6], [24, 4],
         [40, 4], [40, 0], [20, 0], [20, 8]],
        [-16-eps(),16+eps()]),
    for(i=[-36, 40]) ldraw_lin(
        [[4-eps(), -20], [16, -20], [16, -16], [5, -8],
         [5, 8], [16, 16], [16, 20], [4-eps(), 20]],
        [i-4, i], 0)];
solid__s__3822s01 = [
    ldraw_rot([[0,0],[0,-4],[10,-4],[10,0]], o=2),
    ldraw_rot([[6,-4+eps()],[6,-24],[10,-24],[10,-4+eps()]], o=2),
    openscad(translate([0,0,6], o=cube([6+eps(),24,4]))),
    openscad([
        translate([0, -50, -10], o=linear_extrude(4, o=difference([
            square([24, 50]), translate([12,6], o=circle(d=4))]))),
        translate([12, -44, -13-eps()], o=linear_extrude(3+2*eps(),
            o=difference([
                hull([
                    translate([-2, 0], o=square(4)),
                    translate([0, 8], o=circle(d=4))]),
                circle(d=4)]))),
        translate([12, -44, -15], o=linear_extrude(2, o=hull([
            circle(d=4),
            translate([0, 8], o=circle(d=4))])))], 0)];
solid__3821 = [
    [1,16,0,0,0,1,0,0,0,1,0,0,0,1, ldraw_lib__stud(realsolid)],
    [1,16,0,0,0,-1,0,0,0,1,0,0,0,1, ldraw_lib__s__3822s01(realsolid)]];
solid__3822 = [
    [1,16,0,0,0,1,0,0,0,1,0,0,0,1, ldraw_lib__stud(realsolid)],
    [1,16,0,0,0,1,0,0,0,1,0,0,0,1, ldraw_lib__s__3822s01(realsolid)]];
solid__3823 = [
    for(i=[-30,30]) [1,16,i,44,-10,1,0,0,0,-1,0,0,0,1,
        ldraw_lib__stud3(realsolid)],
    for(i=[-20:20:20]) [1,16,i,44,-20,1,0,0,0,-1,0,0,0,1,
        ldraw_lib__stud3(realsolid)],
    for(i=[-30,30]) [1,16,i,0,0,1,0,0,0,1,0,0,0,1,
        ldraw_lib__stud2(realsolid)],
    openscad([
        for(j=[-48, -44]) translate([0, 0, j],
            o=linear_extrude(4+eps(), o=difference([
                hull([
                    for(i=[-30,30]) translate([20,i], o=circle(d=20)),
                    square([20,80], center=true)]),
                square([20, 40], center=true),
                for(i=[-20,20]) translate([-10,i], o=circle(d=20)),
                if(j==-48) [
                    hull([for(i=[-30,30])
                        translate([20,i], o=circle(d=12))]),
                    for(i=[-30,30]) translate([7,i],
                        o=square([26,12], center=true)),
                    for(i=[-20,20]) translate([-10,i],
                        o=square(20, center=true))]]))),
        translate([0, 0, -40], o=multmatrix(
            [[1, 0, -0.5, 0], [0, 1, 0, 0], [0, 0, 1, 0]],
            o=linear_extrude(40, o=difference([
                hull([
                    for(i=[-1,1]) translate([20,i*30], o=circle(d=20)),
                    for(i=[-1,1]) translate([15,i*35], square(10, center=true))]),
                hull([
                    for(i=[-30,30]) translate([20,i], o=circle(d=12)),
                    translate([10,0], square([1,72], center=true))]),
            ])))),
        translate([0, 0, -4], o=linear_extrude(4, o=[
            for(i=[-1, 1]) hull([
                translate([0,30*i], o=circle(d=20)),
                for(j=[-5, 5]) translate([j,(30-j)*i],
                    square(10, center=true))])]))], 2),
    for(i=[-40, 36]) ldraw_lin([[0, -10], [40+eps(), 10+eps()],
        [40+eps(), -10]], [i, i+4], 0)];