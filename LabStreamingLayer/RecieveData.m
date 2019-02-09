close all;
clear all;

%Demo parameters
DATA_POINTS = 4000; %PSD computed on 1000 sample data point
PSD_FREQS = 1:1:100; %PSD over 1 to 30 Hz in 0.5 increments

CHANNEL_OF_INTEREST = 1; %compute PSD on first channel of data

data_buffer = zeros(1, DATA_POINTS); %pre-allocate data

%% instantiate the LSL library
% make sure that everything is on the path and LSL is loaded
if ~exist('arg_define','file')
    addpath(genpath(fileparts(mfilename('fullpath')))); end
if ~exist('env_translatepath','file')
    % standalone case
    lib = lsl_loadlib();
else
    % if we're within BCILAB we want to make sure that the library is also found if the toolbox is compiled
    lib = lsl_loadlib(env_translatepath('dependencies:/liblsl-Matlab/bin'));
end

% resolve a stream...
disp('Resolving an EEG stream...');
result = {};
while isempty(result)
    result = lsl_resolve_byprop(lib,'type','EEG'); end

% create a new inlet
disp('Opening an inlet...');
inlet = lsl_inlet(result{1});

%resolve stream sample rate
FS = inlet.info.nominal_srate();

%create a figure

disp('Now receiving data...');
while true
    % get data from the inlet
    [temp_data,ts] = inlet.pull_chunk();
    
    %extract desired channel
    new_points = temp_data(CHANNEL_OF_INTEREST, :);
    
    %resolve length of data points
    new_length = length(new_points);
    
    %shift into buffer
    data_buffer(1:DATA_POINTS-new_length) = data_buffer(new_length+1:end);
    data_buffer(DATA_POINTS-new_length+1:end) = new_points;
    
    %remove DC offset
    display_buffer = detrend(data_buffer);
    
    %plot raw data
    subplot(2,1,1);
    time = (0:DATA_POINTS-1)/FS;
    plot(time, display_buffer, 'k');
    axis([0 DATA_POINTS/FS -500 500]);
    xlabel('Time (s)');
    ylabel('Signal (\mu V)');
    
    %plot PSD
    subplot(2,1,2);
    [Pxx, Fxx] = pwelch(display_buffer, [], [], PSD_FREQS, FS);
    semilogy(Fxx, sqrt(Pxx), 'k', 'LineWidth', 2);
    xlabel('Frequency (Hz)');
    ylabel('Power (\mu V/Hz ^{1/2}');
    axis([PSD_FREQS(1) PSD_FREQS(end) 1e-1 1e2]);
    grid on;
    
    drawnow;
    
    
end
