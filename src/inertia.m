lhV = spm_vol('../INPUTS/case1/lh.hippoAmygLabels-T1.v21.nii.gz');
[lhY,lhXYZ] = spm_read_vols(lhV);

rhV = spm_vol('../INPUTS/case1/rh.hippoAmygLabels-T1.v21.nii.gz');
[rhY,rhXYZ] = spm_read_vols(rhV);

% mm coords of all voxels in both hippocampi
lh_xyz = lhXYZ(:,lhY(:)>0 & lhY(:)<1000);
rh_xyz = rhXYZ(:,rhY(:)>0 & rhY(:)<1000);
xyz = [lh_xyz rh_xyz];

% mm coords relative to center of mass
com = mean(xyz,2);

x = xyz(1,:) - com(1);
y = xyz(2,:) - com(2);
z = xyz(3,:) - com(3);

% Inertia tensor
Ixx = sum(y.^2 + z.^2);
Iyy = sum(x.^2 + z.^2);
Izz = sum(x.^2 + y.^2);

Ixy = x*y';
Ixz = x*z';
Iyz = y*z';

Imat = [ ...
    Ixx Ixy Ixz;
    Ixy Iyy Iyz;
    Ixz Iyz Izz
    ];

% eig produces right-side eigenvectors so that
%   Imat*V = V*D
% First vector is L/R, second is A/P, third is I/S. This is the order such
% that moment of inertia about each axis is in order from lowest to
% highest.
[V,D] = eig(Imat);


% Apply rotation to COM positioned coords
rxyz = V * [x; y; z];
rx = rxyz(1,:);
ry = rxyz(2,:);
rz = rxyz(3,:);


%% Some plots
figure(1); clf; hold on
plot3(x,y,z,'.k')
plot3(rx,ry,rz,'.y')
xlabel('X')
ylabel('Y')
zlabel('Z')
grid on
axis equal

plot3([0 40*V(1,1)],[0 40*V(1,2)],[0 40*V(1,3)],'-r')
plot3([0 40*V(2,1)],[0 40*V(2,2)],[0 40*V(2,3)],'-g')
plot3([0 40*V(3,1)],[0 40*V(3,2)],[0 40*V(3,3)],'-b')



