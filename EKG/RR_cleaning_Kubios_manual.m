%{
THIS FUNCTION PERFORMS A MANUAL THRESHOLD REJECTION BASED ON KUBIOS HRV SOFTWARE MANUAL.
AS IT CAN BE READ FROM THIS MANUAL:
The threshold based artefact correction algorithm compares every IBI value against a local average
interval. The local average is obtained by median filtering the IBI time series, and thus, the local average
is not affected by single outliers in IBI time series. If an IBI differs from the locale average more than
a specified threshold value, the interval is identified as an artefact and is marked for correction. The
threshold value can be selected from:
• Very low: 0.45 sec (threshold in seconds)
• Low: 0.35 sec
• Medium: 0.25 sec
• Strong: 0.15 sec
• Very strong: 0.05 sec
• Custom, for setting a custom threshold in seconds
For example, the “Medium” correction level will identify all IBIs that are larger/smaller than 0.25 seconds
compared to the local average. The correction is made by replacing the identified artefacts with interpo-
lated values using a cubic spline interpolation. Please note that the thresholds shown above are when
60 bpm hear rate and are adjusted according to mean heart rate (i.e. lower thresholds for higher heart
rate). The correction level should be adjusted individually, because inter-individual difference in HRV
are quite significant and therefore a fixed threshold does not work optimally for all subjects. The optimal
threshold is the lowest correction level which identifies all artefacts but does not identify too many normal
RR intervals as artefacts.
%}


function [RR_corrected, P_corrected] = RR_cleaning_Kubios_manual(RR, P, tr, nbts, plots)
%manual_RR_cleaning_kubios(BRS_data{1}(:,2), [], 0.25, 90, 0)

clc

%nbts is the number of beats to calculate the local median.
%tr is the threshold for the median filter selection

%RR - RR interval time series
%P - Another beat related time series to correct in parallel. For example: beat to beat arterial pressure.
%plots - graphical output

RR = 60./RR; %Convert beats per minute to inter beat interval

if (nargin < 3); plots = 0; end;
if (nargin < 2); P = RR; end;
if isempty(P); P = RR; end;


%Series
dRR = []; mRR = []; thr1 = []; thr2 = [];

if (size(RR, 1) == length(RR)) %Transpose for standarize data treatment
	RR = RR';
end

if (size(P, 1) == length(P))
	P = P';
end

%Calculation of the median filter values
boundaries = [1 : nbts : numel(RR)];
n_steps = numel(boundaries) - mod(numel(boundaries), 2);

artifacts = [];


%Detection of RR artifacts
for i = 1:n_steps - 2
    
    down = boundaries((i-1) + 1);
    up = boundaries((i-1) + 2) - 1;

    med = median(RR(down:up));
    

    for b = down:up
        
        if (RR(b) < (med - tr)) || (RR(b) > (med + tr))
            printf('Artifact has been found on beat number %f\n', b);
            artifacts = [artifacts, b];
        end
        
    end

end


%Artifacts are corrected by cubic spline interpolation
RR = RR(1:boundaries(end)); %Adjust data lenght to the corrected one
order = [1:numel(RR)];
order(artifacts) = [];
RR_ok = RR;
RR_ok(artifacts) = [];
INT = interp1(order, RR_ok, artifacts, 'spline');

RR_corrected = RR;
for i = 1:numel(artifacts)
    RR_corrected(artifacts(i)) = INT(i);
end


%Plots
if plots
    subplot(2,1,1)
    plot(RR);
    subplot(2,1,2)
    plot(RR_corrected, 'r');
end
