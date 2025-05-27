import { Component, EventEmitter, Input, OnInit, Output, signal } from '@angular/core';
import { FilterModel } from '../basic-filter/filter-model';
import { TreeNode } from 'primeng/api';
import { IsmnNetworkService } from '../../../core/services/filter/ismn-network-service';
import { BehaviorSubject } from 'rxjs';
import { DatasetComponentSelectionModel } from '../../../dataset/components/dataset/dataset-component-selection-model';
import { IsmnNetworkDto } from '../../../core/services/filter/ismn-network.dto';
import { ToastService } from '../../../core/services/toast/toast.service';


@Component({
  selector: 'qa-ismn-network-filter',
  templateUrl: './ismn-network-filter.component.html',
  styleUrls: ['./ismn-network-filter.component.scss'],
  standalone: false,
})
export class IsmnNetworkFilterComponent implements OnInit {

  @Input() filterModel$: BehaviorSubject<FilterModel>;
  @Input() datasetModel: DatasetComponentSelectionModel;
  @Output() networkSelectionChanged = new EventEmitter<string>();

  networkSelectorVisible = false;

  networkTree: TreeNode[];
  selectedNetworks: TreeNode[] = [];
  networkFetchError = signal(false);
  errorMessage = 'We could not fetch network for selection, but you can still run validation with default settings. ' +
    'If you keep getting this error, please contact our support team.'

  constructor(public networkService: IsmnNetworkService,
              private toastService: ToastService,) {
  }

  ngOnInit(): void {
    // in case the filter model gets updated externally we need to re-initialize this component
    this.filterModel$.subscribe(model => {
      if (model != null) {
        this.initComponent();
      }
    });
  }

  showNetworkSelector(): void {
    this.networkSelectorVisible = true;
  }


  private buildNetworkTree(networks: IsmnNetworkDto[], networksToBeSelected: string): void {
    this.networkTree = [];
    networks.forEach(net => {
      let continentFound = false;
      for (let i = 0; i < this.networkTree.length; i++) {
        if (net.continent === this.networkTree[i].key) {
          this.networkTree[i].children.push(this.networkDtoToTreeModel(net, this.networkTree[i]));
          continentFound = true;
        }
      }

      if (continentFound === false) {
        const newContinent: TreeNode = {key: net.continent, label: net.continent};
        newContinent.children = [];
        newContinent.children.push(this.networkDtoToTreeModel(net, newContinent));
        this.networkTree.push(newContinent);
      }
    });

    // do preselection
    this.selectedNetworks.length = 0;

    const shouldSelectNetwork = (net: TreeNode): boolean => {
      if (networksToBeSelected === 'ALL') {
        return true;
      } else {
        return networksToBeSelected.includes(net.key);
      }
    };

    this.networkTree.forEach(continent => {
      continent.children.forEach(net => {
        if (shouldSelectNetwork(net)) {
          continent.partialSelected = true;
          // continent.checked = true; // uncomment with angular 17
          this.selectedNetworks.push(net);
        }
      });
    });

    this.updateFilterModel();
  }

  private networkDtoToTreeModel(network: IsmnNetworkDto, parentNode: TreeNode): TreeNode<IsmnNetworkDto> {
    return {key: network.name, label: network.name + ' (' + network.country + ')', data: network, parent: parentNode};
  }

  public onNetworkUnselect(e): void {
    this.updateFilterModel();
  }

  public onNetworkSelect(e): void {
    this.updateFilterModel();
  }

  private updateFilterModel(): void {
    let newSelection = '';
    this.selectedNetworks.forEach(net => {
      if (net.data != null) {  // continent checkboxes does not have data
        if (!newSelection.includes(net.key)) {
          if (newSelection.length > 0) {
            newSelection = newSelection + ',';
          }
          newSelection = newSelection + net.key;
        }
      }
    });

    this.filterModel$.value.parameters$.next(newSelection);
    this.networkSelectionChanged.emit(newSelection);
  }

  private initComponent(): void {
    this.networkService.getNetworksByDatasetVersionId(this.datasetModel.selectedVersion.id)
      .subscribe(this.networkObserver);
  }

  networkObserver = {
    next: data =>  this.buildNetworkTree(data, this.filterModel$.value.parameters$.value),
    error: () => this.onNetworkError()
  }

  onNetworkError(): void{
    this.networkFetchError.set(true);
    this.toastService.showAlertWithHeader('ISMN network problem',this.errorMessage)
  }

}
