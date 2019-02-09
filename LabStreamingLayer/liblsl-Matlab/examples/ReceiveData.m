close all;
clear all;

%PSD parameters
CHANNEL = 1; %use the first channel of the data stream
BUFLEN = 2000; %1000 sample buffer
FREQS = 1:1:80; %compute PSD over 1 to 30 Hz in 1 Hz increments

%create data buffer vector
eeg_data = zeros(1, BUFLEN);

%% instantiate the LSL library
disp('Loading the library...');
lib = lsl_loadlib();

% resolve a stream...
disp('Resolving an EEG stream...');
result = {};
while isempty(result)
    result = lsl_resolve_byprop(lib,'type','EEG'); end

% create a new inlet
disp('Opening an inlet...');
inlet = lsl_inlet(result{1});

%grab stream sample rate
FS = inlet.info.nominal_srate();

disp('Now receiving data...');

figure;

while true
    % get data chunk from the inlet
    [chunkdata,timestamps] = inlet.pull_chunk();
    
    %pull out channel of interest and find length
    temp_new_data = chunkdata(CHANNEL, :);
    num_new_samples = length(temp_new_data)
    
    %update buffer
    eeg_data(1:BUFLEN-num_new_samples) = eeg_data(num_new_samples+1:end);
    eeg_data(BUFLEN-num_new_samples+1:end) = temp_new_data;
    
    %compute psd
    [Pxx, Fxx] = pwelch(eeg_data, [], [], FREQS, FS);
    
    subplot(2,1,1);
    plot( (0:(length(eeg_data)-1))/FS, detrend(eeg_data), 'k');
    ylabel('Signal (\mu V)');
    xlabel('Time (s)');
    
    subplot(2,1,2);
    loglog(Fxx, sqrt(Pxx), 'k');
    xlabel('Frequency (Hz)');
    ylabel('Power \mu V/Hz^{0.5}');
    grid on;
    
    drawnow;
    
end