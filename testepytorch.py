import torch

# Verifique se a GPU está disponível
if torch.cuda.is_available():
    device = torch.device('cuda')
    print('GPU está disponível e será utilizada.')
else:
    device = torch.device('cpu')
    print('GPU não está disponível, a CPU será utilizada.')

# Crie um tensor e mova-o para a GPU
x = torch.randn(5, 3).to(device)
print(x)
