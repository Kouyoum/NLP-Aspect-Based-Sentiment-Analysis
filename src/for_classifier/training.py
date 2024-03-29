import torch
import torch.nn as nn
from tqdm import tqdm
import numpy as np

# train functions

def train_epoch(
    model, 
    data_loader, 
    loss_fn, 
    optimizer, 
    device, 
    scheduler, 
    n_examples):
    """ 
    Trains the BERT model for one epoch.
    Returns the accuracy on the training set, and the average cross-entropy loss (over batches)
    """
    model = model.train()

    losses = []
    correct_predictions = 0
    
    for d in tqdm(data_loader):
      input_ids = d["input_ids"].to(device)
      attention_mask = d["attention_mask"].to(device)
      targets = d["targets"].to(device)
      
      outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask
      )
      
      _, preds = torch.max(outputs, dim=1)
      loss = loss_fn(outputs, targets)

      correct_predictions += torch.sum(preds == targets)
      losses.append(loss.item())

      loss.backward()
      nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
      optimizer.step()
      scheduler.step()
      optimizer.zero_grad()
    
    return correct_predictions.double() / n_examples, np.mean(losses)


def eval_epoch(model, data_loader, loss_fn, device, n_examples):
    """
    Runs the evaluation on the validation set.
    Returns the accuracy and average Cross-entropy loss (over batches). 
    """
    model = model.eval()

    losses = []
    correct_predictions = 0

    with torch.no_grad():
      for d in tqdm(data_loader):
        input_ids = d["input_ids"].to(device)
        attention_mask = d["attention_mask"].to(device)
        targets = d["targets"].to(device)

        outputs = model(
          input_ids=input_ids,
          attention_mask=attention_mask
        )
        _, preds = torch.max(outputs, dim=1)

        loss = loss_fn(outputs, targets)

        correct_predictions += torch.sum(preds == targets)
        losses.append(loss.item())

    return correct_predictions.double() / n_examples, np.mean(losses) 