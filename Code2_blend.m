% Phase Diagram Analysis for Polymer:SMA Blends  
clc; clear; close all;  

%% Input Parameters  
N_A = input('Enter degree of polymerization for Polymer A N_A: ');  
N_B = input('Enter degree of polymerization for Polymer B N_B: ');  
chi_start = input('Enter χ lower bound: ');  
chi_end = input('Enter χ upper bound: ');  
chi_step = input('Enter χ step size: ');  
chi_range = chi_start:chi_step:chi_end;  

%% Computational Parameters  
phi = linspace(0.0001, 0.9999, 5000)'; % Composition range [0,1] 
dx = phi(2) - phi(1); % Composition step  

%% Data Containers Initialization  
min_phi = cell(length(chi_range),1); % Free energy minima  
spinodal_phi = cell(length(chi_range),1);% Free energy minima  

%% Main Computation Loop  
for k = 1:length(chi_range)  
chi = chi_range(k);  
% Calculate free energy density  
term1 = (phi .* log(phi)) / N_A;  
term2 = ((1-phi) .* log(1-phi)) / N_B;  
term3 = chi .* phi .* (1-phi);  
DeltaG = term1 + term2 + term3;  
% Local minima detection (manual extremum search)  
minima = [];  
for i = 2:length(DeltaG)-1  
if DeltaG(i) < DeltaG(i-1) && DeltaG(i) < DeltaG(i+1)  
minima = [minima; phi(i)];  
end  
end  
min_phi{k} = minima;  
% Spinodal detection via second derivative  
dG = gradient(DeltaG, dx);  
d2G = gradient(dG, dx);  
% Zero-crossing detection  
cross_points = [];  
for i = 2:length(d2G)-1  
if d2G(i)*d2G(i+1) < 0  
t = -d2G(i)/(d2G(i+1)-d2G(i));  
x0 = phi(i) + t*dx;  
cross_points = [cross_points; x0];  
end  
end  
spinodal_phi{k} = sort(cross_points);  
end  

%% Data Export Routines  
% Export free energy minima  
export_min = [];  
for k = 1:length(chi_range)  
if ~isempty(min_phi{k})  
export_min = [export_min; [chi_range(k)*ones(size(min_phi{k})), min_phi{k}]];  
end  
end  
writecell({'Chi', 'Phi'}, 'extremum_data.csv');  
writematrix(export_min, 'extremum_data.csv', 'WriteMode', 'append');  

% Export spinodal points  
export_spinodal = [];  
for k = 1:length(chi_range)  
if ~isempty(spinodal_phi{k})  
export_spinodal = [export_spinodal; [chi_range(k)*ones(size(spinodal_phi{k})), spinodal_phi{k}]];  
end  
end  
writecell({'Chi', 'Phi'}, 'spinodal_data.csv');  
writematrix(export_spinodal, 'spinodal_data.csv', 'WriteMode', 'append');  

%% Visualization Toolkit  
% Color  
cmap = jet(length(chi_range));  

% Figure 1: Free Energy Profiles  
figure('Position', [100 100 1200 400])  
subplot(1,3,1)  
hold on;  
for k = 1:length(chi_range)  
plot(phi, (phi.*log(phi))/N_A + ((1-phi).*log(1-phi))/N_B + ...  
chi_range(k).*phi.*(1-phi), 'Color', cmap(k,:))  
end  
xlabel('\phi');   
ylabel('\Delta G_{mix}/(k_B T)');  
title('(a) Free Energy Landscape');  
colormap(jet);   
h = colorbar('Ticks', linspace(0,1,5), 'TickLabels', linspace(chi_start,chi_end,5));  
h.Label.String = 'χ';  
grid on;  

% Figure 2: Phase Diagram - Minima  
subplot(1,3,2)  
hold on;  
for k = 1:length(chi_range)  
if ~isempty(min_phi{k})  
scatter(min_phi{k}, chi_range(k)*ones(size(min_phi{k})), 30, cmap(k,:), 'filled')  
end  
end  
xlabel('\phi_{min}');  
ylabel('χ');  
title(' (b) Phase Diagram - Minima');  
grid on;  
xlim([0 1])  

% Figure 3: Spinodal Diagram  
subplot(1,3,3)  
hold on;  
for k = 1:length(chi_range)  
if ~isempty(spinodal_phi{k})  
scatter(spinodal_phi{k}, chi_range(k)*ones(size(spinodal_phi{k})), 30, cmap(k,:), 'filled')  
end  
end  

% Theoretical critical point  
chi_c = 0.5*(1/sqrt(N_A) + 1/sqrt(N_B))^2;  
plot(0.5, chi_c, 'k*', 'MarkerSize', 10)  
xlabel('Spinodal points \phi');  
ylabel('χ');  
title(' (c) Spinodal Diagram');  
grid on;  
xlim([0 1])  

% Formatting  
set(findall(gcf,'Type','axes'), 'FontSize', 10, 'Box', 'on')  

disp('Data files created:');  
disp('1. extremum_data.csv - Free energy minima coordinates');  
disp('2. spinodal_data.csv - Spinodal points coordinates');
