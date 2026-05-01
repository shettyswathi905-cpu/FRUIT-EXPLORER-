import torch
import torch.nn as nn
import torch.nn.functional as F

class FruitClassifierCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(FruitClassifierCNN, self).__init__()
        # Input: 3 channels (RGB), 224x224 image
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        # Calculate feature map size after 3 poolings:
        # 224 -> 112 -> 56 -> 28
        self.fc1 = nn.Linear(128 * 28 * 28, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        
        # Flatten
        x = x.view(-1, 128 * 28 * 28)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

if __name__ == "__main__":
    # Test model shape
    model = FruitClassifierCNN(num_classes=5)
    test_tensor = torch.randn(1, 3, 224, 224)
    out = model(test_tensor)
    print("Output shape from forward pass:", out.shape)
