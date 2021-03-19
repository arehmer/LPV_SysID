% Load identified Vertex Systems
load('VertexSystemsSilverbox.mat') 


% Specify dimensions of problem
nx = 2;
nw = 1;
ny = 1;
nu = 1;


% In this control problem, certain matrices are fixed
B1  = zeros(nx,nw);
D11 = eye(ny,nw);
D12 = zeros(ny,nu);
D21 = zeros(ny,nu);
D22 = zeros(ny,nu);

r = sdpvar(1,1);

R = sdpvar(nx,nx,'symmetric');
S = sdpvar(nx,nx,'symmetric');

LMI = [[R,eye(nx);eye(nx),S] <= 0];


VertexSystems = {'S1','S2','S3','S4'};

for vertex = [1:4]
    
    system = eval(VertexSystems{vertex});
    
    A  = system{1};
    B2 = system{2};
    C1 = system{3};
    C2 = system{3};
    
    
    
    
    NR = null([B2',D12']);
    NS = null([C2,D21]);

    MR = [A*R*A'-R,   A*R*C1',               B1;
          C1*R*A',     -r*eye(ny)+C1*R*C1',  D11;
          B1',        D11',                  -r*eye(nw)];

    MS = [A'*S*A-S,   A'*S*B1,               C1';
         B1'*S*A,     -r*eye(ny)+B1'*S*B1,   D11';
         C1,          D11,                   -r*eye(nw)];
 
    NR = [NR,           zeros(3,1);
          zeros(1,2),   eye(1) ];
    
    NS = [NS,       zeros(3,1);
            zeros(1,2), eye(1) ];
        
        
    LMI = [LMI,[NR'*MR*NR<=0]];
    LMI = [LMI,[NS'*MS*NS<=0]];
    
end

optimize(LMI,r)


% Calculate wo full column rank matrices M and N

% M = chol(eye(nx)-double(R)*double(S));
[M,N] = qr(eye(nx)-double(R)*double(S));